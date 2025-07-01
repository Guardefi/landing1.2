#!/bin/bash
# Scorpius Load Test and Cost Analysis Automation
# Runs k6 load tests and generates HPA scaling recommendations

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TEST_DIR="$PROJECT_ROOT/tests/performance"
RESULTS_DIR="$PROJECT_ROOT/load-test-results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Default values
BASE_URL="${BASE_URL:-http://localhost:8000}"
WS_URL="${WS_URL:-ws://localhost:8000}"
TEST_USERNAME="${TEST_USERNAME:-admin@scorpius.com}"
TEST_PASSWORD="${TEST_PASSWORD:-admin123}"
SCENARIO="${SCENARIO:-baseline}"
DURATION="${DURATION:-5m}"
VUS="${VUS:-10}"
GENERATE_VISUALIZATIONS="${GENERATE_VISUALIZATIONS:-true}"
SLACK_WEBHOOK="${SLACK_WEBHOOK:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check dependencies
check_dependencies() {
    log_info "Checking dependencies..."
    
    local missing_deps=()
    
    if ! command -v k6 &> /dev/null; then
        missing_deps+=("k6")
    fi
    
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    fi
    
    if ! command -v jq &> /dev/null; then
        missing_deps+=("jq")
    fi
    
    if ! command -v curl &> /dev/null; then
        missing_deps+=("curl")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "Missing dependencies: ${missing_deps[*]}"
        log_info "Please install missing dependencies and try again"
        exit 1
    fi
    
    # Check Python dependencies
    if ! python3 -c "import matplotlib, pandas, numpy" 2>/dev/null; then
        log_warning "Python visualization dependencies missing. Installing..."
        pip3 install matplotlib pandas numpy || {
            log_warning "Could not install Python dependencies. Visualizations will be skipped."
            GENERATE_VISUALIZATIONS="false"
        }
    fi
    
    log_success "All dependencies satisfied"
}

# Setup test environment
setup_test_environment() {
    log_info "Setting up test environment..."
    
    # Create results directory
    mkdir -p "$RESULTS_DIR"
    
    # Create test-specific directory
    TEST_RUN_DIR="$RESULTS_DIR/run_${TIMESTAMP}"
    mkdir -p "$TEST_RUN_DIR"
    
    # Health check
    log_info "Performing health check on $BASE_URL..."
    if ! curl -sf "$BASE_URL/health" > /dev/null; then
        log_error "Health check failed. Is the Scorpius platform running?"
        exit 1
    fi
    
    log_success "Test environment ready"
}

# Run k6 load test
run_load_test() {
    local scenario="$1"
    local output_file="$TEST_RUN_DIR/k6-results-${scenario}.json"
    
    log_info "Running k6 load test - scenario: $scenario"
    
    # Set environment variables for k6
    export BASE_URL="$BASE_URL"
    export WS_URL="$WS_URL"
    export TEST_USERNAME="$TEST_USERNAME"
    export TEST_PASSWORD="$TEST_PASSWORD"
    export SCENARIO="$scenario"
    
    # Run k6 test
    local k6_cmd="k6 run"
    k6_cmd+=" --out json=$output_file"
    k6_cmd+=" --summary-export=$TEST_RUN_DIR/k6-summary-${scenario}.json"
    
    # Scenario-specific parameters
    case "$scenario" in
        "baseline")
            k6_cmd+=" --vus $VUS --duration $DURATION"
            ;;
        "ramp_up")
            k6_cmd+=" --stage 1m:10,2m:50,2m:100,1m:0"
            ;;
        "spike")
            k6_cmd+=" --stage 30s:10,10s:100,1m:100,10s:10,30s:10"
            ;;
        "soak")
            k6_cmd+=" --vus 50 --duration 10m"
            ;;
        *)
            log_error "Unknown scenario: $scenario"
            exit 1
            ;;
    esac
    
    k6_cmd+=" $TEST_DIR/k6-mempool-stress.js"
    
    log_info "Executing: $k6_cmd"
    
    if eval "$k6_cmd"; then
        log_success "Load test completed successfully"
        return 0
    else
        log_error "Load test failed"
        return 1
    fi
}

# Analyze test results
analyze_results() {
    local scenario="$1"
    local results_file="$TEST_RUN_DIR/k6-results-${scenario}.json"
    local analysis_file="$TEST_RUN_DIR/analysis-${scenario}.json"
    
    log_info "Analyzing test results for scenario: $scenario"
    
    if [ ! -f "$results_file" ]; then
        log_error "Results file not found: $results_file"
        return 1
    fi
    
    # Convert k6 output to analysis format
    log_info "Converting k6 output format..."
    python3 << EOF
import json
import sys

# Read k6 streaming JSON output and convert to summary format
results = {"metrics": {}, "thresholds": {}}
metrics_data = {}

try:
    with open("$results_file", "r") as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                if data["type"] == "Point":
                    metric_name = data["metric"]
                    if metric_name not in metrics_data:
                        metrics_data[metric_name] = []
                    metrics_data[metric_name].append(data["data"]["value"])

    # Calculate summary statistics
    for metric, values in metrics_data.items():
        if values:
            results["metrics"][metric] = {
                "count": len(values),
                "rate": sum(values) / len(values) if metric.endswith("_rate") else 0,
                "avg": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "p50": sorted(values)[int(len(values) * 0.5)],
                "p90": sorted(values)[int(len(values) * 0.9)],
                "p95": sorted(values)[int(len(values) * 0.95)],
                "p99": sorted(values)[int(len(values) * 0.99)]
            }

    # Add test duration (estimated)
    results["test_duration"] = len(metrics_data.get("http_reqs", [1])) * 1000  # Rough estimate

    with open("${results_file}.processed", "w") as f:
        json.dump(results, f, indent=2)

except Exception as e:
    print(f"Error processing k6 results: {e}", file=sys.stderr)
    sys.exit(1)
EOF
    
    # Run cost model analysis
    local analyzer_args=""
    if [ "$GENERATE_VISUALIZATIONS" = "true" ]; then
        analyzer_args+=" --visualizations"
    fi
    
    if python3 "$TEST_DIR/cost-model-analyzer.py" "${results_file}.processed" --output "$analysis_file" $analyzer_args; then
        log_success "Analysis completed successfully"
        return 0
    else
        log_error "Analysis failed"
        return 1
    fi
}

# Generate comprehensive report
generate_report() {
    local scenario="$1"
    local analysis_file="$TEST_RUN_DIR/analysis-${scenario}.json"
    local report_file="$TEST_RUN_DIR/comprehensive-report-${scenario}.md"
    
    log_info "Generating comprehensive report..."
    
    if [ ! -f "$analysis_file" ]; then
        log_error "Analysis file not found: $analysis_file"
        return 1
    fi
    
    # Generate Markdown report
    python3 << EOF
import json
import sys
from datetime import datetime

try:
    with open("$analysis_file", "r") as f:
        analysis = json.load(f)

    report = f"""# Scorpius Load Test Report - {scenario.upper()}

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Scenario:** $scenario
**Test Duration:** {analysis['detailed_analysis']['test_summary']['test_duration_minutes']:.1f} minutes

## Executive Summary

{analysis['executive_summary']['key_findings'][0] if analysis['executive_summary']['key_findings'] else 'No key findings available'}

### Current Performance
- **RPS:** {analysis['executive_summary']['current_performance']['rps']:.1f}
- **CPU Utilization:** {analysis['executive_summary']['current_performance']['cpu_utilization']:.1f}%
- **Cost per Hour:** \${analysis['executive_summary']['current_performance']['cost_per_hour']:.2f}
- **P95 Latency:** {analysis['executive_summary']['current_performance']['avg_latency_ms']:.0f}ms

### Estimated Monthly Savings
\${analysis['executive_summary']['estimated_savings']:.2f}

## Key Findings
"""

    for finding in analysis['executive_summary']['key_findings']:
        report += f"- {finding}\n"

    report += f"""
## Immediate Actions Required
"""

    for action in analysis['executive_summary']['immediate_actions']:
        report += f"- {action}\n"

    report += f"""
## Scaling Recommendations

### Top 3 Recommendations
"""

    for i, rec in enumerate(analysis['recommendations'][:3], 1):
        report += f"""
#### {i}. {rec['recommendation']}
- **Recommended Replicas:** {rec['replicas']}
- **Monthly Cost Impact:** \${rec['cost_impact_monthly']:.2f}
- **Confidence:** {rec['confidence']:.0%}
- **Implementation Complexity:** {rec['implementation_complexity']}
"""

    report += f"""
## Performance Analysis

### Resource Utilization
- **CPU Average:** {analysis['detailed_analysis']['performance_metrics']['cpu_utilization_avg']:.1f}%
- **CPU P95:** {analysis['detailed_analysis']['performance_metrics']['cpu_utilization_p95']:.1f}%
- **Memory Average:** {analysis['detailed_analysis']['performance_metrics']['memory_usage_avg_mb']:.0f}MB
- **Memory P95:** {analysis['detailed_analysis']['performance_metrics']['memory_usage_p95_mb']:.0f}MB

### Latency Metrics
- **P50:** {analysis['detailed_analysis']['performance_metrics']['latency_p50']:.0f}ms
- **P90:** {analysis['detailed_analysis']['performance_metrics']['latency_p90']:.0f}ms
- **P95:** {analysis['detailed_analysis']['performance_metrics']['latency_p95']:.0f}ms
- **P99:** {analysis['detailed_analysis']['performance_metrics']['latency_p99']:.0f}ms

## Cost Analysis

### Current Costs
- **CPU Cost per Hour:** \${analysis['detailed_analysis']['cost_analysis']['cpu_cost_per_hour']:.3f}
- **Memory Cost per Hour:** \${analysis['detailed_analysis']['cost_analysis']['memory_cost_per_hour']:.3f}
- **Total Cost per Hour:** \${analysis['detailed_analysis']['cost_analysis']['total_cost_per_hour']:.3f}
- **Cost per RPS:** \${analysis['detailed_analysis']['cost_analysis']['cost_per_rps']:.4f}
- **Efficiency Score:** {analysis['detailed_analysis']['cost_analysis']['efficiency_score']:.1f}

### Optimization Opportunities
"""

    for opp in analysis['cost_optimization']['optimization_opportunities']:
        report += f"""
#### {opp['area']}
- **Potential Savings:** \${opp['potential_savings']:.2f}/month
- **Description:** {opp['description']}
"""

    report += f"""
## SLA Compliance

### Latency SLA
- **Target:** {analysis['detailed_analysis']['sla_compliance']['latency_sla']['target']}ms
- **Actual:** {analysis['detailed_analysis']['sla_compliance']['latency_sla']['actual']:.0f}ms
- **Status:** {'✅ COMPLIANT' if analysis['detailed_analysis']['sla_compliance']['latency_sla']['compliant'] else '❌ NON-COMPLIANT'}

### Error Rate SLA
- **Target:** {analysis['detailed_analysis']['sla_compliance']['error_rate_sla']['target']:.1%}
- **Actual:** {analysis['detailed_analysis']['sla_compliance']['error_rate_sla']['actual']:.1%}
- **Status:** {'✅ COMPLIANT' if analysis['detailed_analysis']['sla_compliance']['error_rate_sla']['compliant'] else '❌ NON-COMPLIANT'}

## Monitoring Recommendations

### Recommended Alerts
"""

    for alert in analysis['monitoring_alerts']:
        report += f"""
- **{alert['metric']}:** Threshold {alert['threshold']}, Action: {alert['action']}
"""

    report += f"""
## Files Generated
- Load test results: `k6-results-{scenario}.json`
- Analysis data: `analysis-{scenario}.json`
- Performance charts: `analysis-{scenario}_performance.png`
- Cost analysis: `analysis-{scenario}_cost.png`
- Scaling recommendations: `analysis-{scenario}_scaling.png`

---
*Report generated by Scorpius Load Test Analyzer v1.0*
"""

    with open("$report_file", "w") as f:
        f.write(report)

    print("Report generated successfully")

except Exception as e:
    print(f"Error generating report: {e}", file=sys.stderr)
    sys.exit(1)
EOF
    
    if [ $? -eq 0 ]; then
        log_success "Comprehensive report generated: $report_file"
        return 0
    else
        log_error "Report generation failed"
        return 1
    fi
}

# Send notifications
send_notifications() {
    local scenario="$1"
    local analysis_file="$TEST_RUN_DIR/analysis-${scenario}.json"
    
    if [ -n "$SLACK_WEBHOOK" ] && [ -f "$analysis_file" ]; then
        log_info "Sending Slack notification..."
        
        local summary=$(python3 -c "
import json
with open('$analysis_file', 'r') as f:
    data = json.load(f)
    summary = data['executive_summary']
    print(f\"RPS: {summary['current_performance']['rps']:.1f}, CPU: {summary['current_performance']['cpu_utilization']:.1f}%, Cost: \${summary['current_performance']['cost_per_hour']:.2f}/hr\")
")
        
        local payload=$(cat << EOF
{
    "text": "🚀 Scorpius Load Test Completed",
    "attachments": [
        {
            "color": "good",
            "fields": [
                {
                    "title": "Scenario",
                    "value": "$scenario",
                    "short": true
                },
                {
                    "title": "Performance",
                    "value": "$summary",
                    "short": true
                },
                {
                    "title": "Report",
                    "value": "Detailed analysis available in test results",
                    "short": false
                }
            ]
        }
    ]
}
EOF
)
        
        if curl -X POST -H 'Content-type: application/json' --data "$payload" "$SLACK_WEBHOOK" > /dev/null 2>&1; then
            log_success "Slack notification sent"
        else
            log_warning "Failed to send Slack notification"
        fi
    fi
}

# Main execution
main() {
    log_info "Starting Scorpius Load Test and Analysis Pipeline"
    log_info "Timestamp: $TIMESTAMP"
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --scenario)
                SCENARIO="$2"
                shift 2
                ;;
            --duration)
                DURATION="$2"
                shift 2
                ;;
            --vus)
                VUS="$2"
                shift 2
                ;;
            --base-url)
                BASE_URL="$2"
                shift 2
                ;;
            --no-visualizations)
                GENERATE_VISUALIZATIONS="false"
                shift
                ;;
            --slack-webhook)
                SLACK_WEBHOOK="$2"
                shift 2
                ;;
            --help)
                cat << EOF
Usage: $0 [OPTIONS]

Options:
    --scenario SCENARIO         Test scenario (baseline, ramp_up, spike, soak) [default: baseline]
    --duration DURATION         Test duration [default: 5m]
    --vus VUS                  Virtual users [default: 10]
    --base-url URL             Base URL for testing [default: http://localhost:8000]
    --no-visualizations        Skip generating visualization charts
    --slack-webhook URL        Slack webhook URL for notifications
    --help                     Show this help message

Environment Variables:
    BASE_URL                   Base URL for testing
    WS_URL                     WebSocket URL for testing
    TEST_USERNAME              Test user username
    TEST_PASSWORD              Test user password
    SLACK_WEBHOOK              Slack webhook URL

Examples:
    $0 --scenario baseline --duration 10m --vus 20
    $0 --scenario spike --slack-webhook https://hooks.slack.com/...
EOF
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Execute pipeline
    check_dependencies
    setup_test_environment
    
    if run_load_test "$SCENARIO"; then
        if analyze_results "$SCENARIO"; then
            generate_report "$SCENARIO"
            send_notifications "$SCENARIO"
            
            log_success "Load test and analysis pipeline completed successfully!"
            log_info "Results available in: $TEST_RUN_DIR"
            
            # Display quick summary
            if [ -f "$TEST_RUN_DIR/analysis-${SCENARIO}.json" ]; then
                log_info "Quick Summary:"
                python3 -c "
import json
with open('$TEST_RUN_DIR/analysis-${SCENARIO}.json', 'r') as f:
    data = json.load(f)
    summary = data['executive_summary']
    print(f'  RPS: {summary[\"current_performance\"][\"rps\"]:.1f}')
    print(f'  CPU: {summary[\"current_performance\"][\"cpu_utilization\"]:.1f}%')
    print(f'  Cost: \${summary[\"current_performance\"][\"cost_per_hour\"]:.2f}/hour')
    print(f'  Potential Monthly Savings: \${summary[\"estimated_savings\"]:.2f}')
"
            fi
        else
            log_error "Analysis failed"
            exit 1
        fi
    else
        log_error "Load test failed"
        exit 1
    fi
}

# Execute main function
main "$@"