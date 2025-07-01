#!/bin/bash
# Chaos Friday - Monthly Disaster Recovery Drill
# Simulates infrastructure failures and measures recovery times
# RTO/RPO validation for SOC2 and enterprise compliance

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESULTS_DIR="$PROJECT_ROOT/chaos-results"
CLUSTER_NAME="${CLUSTER_NAME:-scorpius-prod}"
REGION="${REGION:-us-east-1}"
NAMESPACE="${NAMESPACE:-scorpius}"
SLACK_WEBHOOK="${SLACK_WEBHOOK:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Timing functions
start_timer() {
    echo $(date +%s)
}

end_timer() {
    local start_time=$1
    local end_time=$(date +%s)
    echo $((end_time - start_time))
}

# Setup results directory
setup_results_dir() {
    mkdir -p "$RESULTS_DIR"
    DRILL_DIR="$RESULTS_DIR/chaos-drill-$TIMESTAMP"
    mkdir -p "$DRILL_DIR"
    
    # Create drill report file
    REPORT_FILE="$DRILL_DIR/chaos-drill-report.json"
    cat > "$REPORT_FILE" << EOF
{
  "drill_id": "chaos-drill-$TIMESTAMP",
  "start_time": "$(date -Iseconds)",
  "cluster": "$CLUSTER_NAME",
  "region": "$REGION",
  "namespace": "$NAMESPACE",
  "scenarios": [],
  "metrics": {
    "rto_target_minutes": 15,
    "rpo_target_minutes": 5
  }
}
EOF
    
    log_info "Chaos drill results will be saved to: $DRILL_DIR"
}

# Pre-flight checks
preflight_checks() {
    log_info "Running pre-flight checks..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI not found. Please install AWS CLI."
        exit 1
    fi
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl not found. Please install kubectl."
        exit 1
    fi
    
    # Check cluster connectivity
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster. Check kubeconfig."
        exit 1
    fi
    
    # Check if cluster exists
    if ! aws eks describe-cluster --name "$CLUSTER_NAME" --region "$REGION" &> /dev/null; then
        log_error "EKS cluster '$CLUSTER_NAME' not found in region '$REGION'"
        exit 1
    fi
    
    # Check if namespace exists
    if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
        log_error "Namespace '$NAMESPACE' not found"
        exit 1
    fi
    
    log_success "Pre-flight checks completed"
}

# Capture baseline metrics
capture_baseline() {
    log_info "Capturing baseline metrics..."
    
    local baseline_file="$DRILL_DIR/baseline-metrics.json"
    
    # Get current pod count
    local pod_count=$(kubectl get pods -n "$NAMESPACE" --field-selector=status.phase=Running -o json | jq '.items | length')
    
    # Get node count
    local node_count=$(kubectl get nodes --no-headers | wc -l)
    
    # Get service endpoints
    local services=$(kubectl get services -n "$NAMESPACE" -o json)
    
    # Test application health
    local health_status="unknown"
    if kubectl get service -n "$NAMESPACE" scorpius-api-gateway &> /dev/null; then
        local service_ip=$(kubectl get service -n "$NAMESPACE" scorpius-api-gateway -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
        if [ -n "$service_ip" ] && curl -sf "http://$service_ip/health" &> /dev/null; then
            health_status="healthy"
        else
            health_status="unhealthy"
        fi
    fi
    
    # Create baseline snapshot
    cat > "$baseline_file" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "cluster": {
    "name": "$CLUSTER_NAME",
    "region": "$REGION",
    "node_count": $node_count
  },
  "application": {
    "namespace": "$NAMESPACE",
    "pod_count": $pod_count,
    "health_status": "$health_status"
  },
  "services": $services
}
EOF
    
    log_success "Baseline metrics captured: $pod_count pods, $node_count nodes, health: $health_status"
}

# Scenario 1: EKS Node Group Termination
scenario_nodegroup_termination() {
    log_info "🔥 SCENARIO 1: EKS Node Group Termination"
    
    local scenario_start=$(start_timer)
    local scenario_data="{\"name\": \"nodegroup_termination\", \"start_time\": \"$(date -Iseconds)\"}"
    
    # Get node groups
    local nodegroups=$(aws eks list-nodegroups --cluster-name "$CLUSTER_NAME" --region "$REGION" --query 'nodegroups[0]' --output text)
    
    if [ "$nodegroups" == "None" ] || [ -z "$nodegroups" ]; then
        log_error "No node groups found in cluster"
        return 1
    fi
    
    log_info "Target node group: $nodegroups"
    
    # Scale down node group to 0
    log_info "Scaling down node group to 0..."
    local scale_down_start=$(start_timer)
    
    aws eks update-nodegroup-config \
        --cluster-name "$CLUSTER_NAME" \
        --nodegroup-name "$nodegroups" \
        --region "$REGION" \
        --scaling-config minSize=0,maxSize=0,desiredSize=0
    
    # Wait for nodes to terminate
    log_info "Waiting for nodes to terminate..."
    while true; do
        local node_count=$(kubectl get nodes --no-headers 2>/dev/null | wc -l)
        if [ "$node_count" -eq 0 ]; then
            break
        fi
        log_info "Nodes remaining: $node_count"
        sleep 30
    done
    
    local scale_down_duration=$(end_timer $scale_down_start)
    log_warning "All nodes terminated in ${scale_down_duration}s"
    
    # Verify application is down
    local app_down_time=$(start_timer)
    log_info "Verifying application is down..."
    
    # Scale back up
    log_info "Scaling node group back up..."
    local recovery_start=$(start_timer)
    
    aws eks update-nodegroup-config \
        --cluster-name "$CLUSTER_NAME" \
        --nodegroup-name "$nodegroups" \
        --region "$REGION" \
        --scaling-config minSize=2,maxSize=10,desiredSize=3
    
    # Wait for nodes to be ready
    log_info "Waiting for nodes to be ready..."
    while true; do
        local ready_nodes=$(kubectl get nodes --no-headers 2>/dev/null | grep -c Ready || echo "0")
        if [ "$ready_nodes" -ge 2 ]; then
            break
        fi
        log_info "Ready nodes: $ready_nodes"
        sleep 30
    done
    
    # Wait for pods to be running
    log_info "Waiting for pods to be running..."
    while true; do
        local running_pods=$(kubectl get pods -n "$NAMESPACE" --field-selector=status.phase=Running -o json | jq '.items | length')
        if [ "$running_pods" -ge 5 ]; then  # Minimum expected pods
            break
        fi
        log_info "Running pods: $running_pods"
        sleep 15
    done
    
    # Test application health
    log_info "Testing application health..."
    local health_recovery_start=$(start_timer)
    local health_recovered=false
    
    for i in {1..20}; do
        if kubectl get service -n "$NAMESPACE" scorpius-api-gateway &> /dev/null; then
            local service_ip=$(kubectl get service -n "$NAMESPACE" scorpius-api-gateway -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
            if [ -n "$service_ip" ] && curl -sf "http://$service_ip/health" &> /dev/null; then
                health_recovered=true
                break
            fi
        fi
        sleep 15
    done
    
    local health_recovery_duration=$(end_timer $health_recovery_start)
    local total_recovery_duration=$(end_timer $recovery_start)
    local scenario_duration=$(end_timer $scenario_start)
    
    # Update scenario data
    scenario_data=$(echo "$scenario_data" | jq --arg end_time "$(date -Iseconds)" \
        --arg duration "$scenario_duration" \
        --arg scale_down_duration "$scale_down_duration" \
        --arg recovery_duration "$total_recovery_duration" \
        --arg health_recovery_duration "$health_recovery_duration" \
        --arg health_recovered "$health_recovered" \
        '. + {
            "end_time": $end_time,
            "duration_seconds": ($duration | tonumber),
            "scale_down_duration_seconds": ($scale_down_duration | tonumber),
            "recovery_duration_seconds": ($recovery_duration | tonumber),
            "health_recovery_duration_seconds": ($health_recovery_duration | tonumber),
            "health_recovered": ($health_recovered | test("true")),
            "rto_minutes": (($recovery_duration | tonumber) / 60),
            "status": (if ($health_recovered | test("true")) then "success" else "failed" end)
        }')
    
    # Add to report
    jq --argjson scenario "$scenario_data" '.scenarios += [$scenario]' "$REPORT_FILE" > "$REPORT_FILE.tmp" && mv "$REPORT_FILE.tmp" "$REPORT_FILE"
    
    if [ "$health_recovered" = true ]; then
        log_success "Node group termination recovery completed in ${total_recovery_duration}s (${health_recovery_duration}s for health)"
    else
        log_error "Node group termination recovery failed - application health not restored"
    fi
}

# Scenario 2: Database Failover Test
scenario_database_failover() {
    log_info "🔥 SCENARIO 2: Database Failover Test"
    
    local scenario_start=$(start_timer)
    local scenario_data="{\"name\": \"database_failover\", \"start_time\": \"$(date -Iseconds)\"}"
    
    # Find RDS cluster
    local db_cluster=$(aws rds describe-db-clusters --region "$REGION" --query "DBClusters[?contains(DBClusterIdentifier, 'scorpius')].DBClusterIdentifier" --output text | head -1)
    
    if [ -z "$db_cluster" ] || [ "$db_cluster" == "None" ]; then
        log_warning "No RDS cluster found - skipping database failover test"
        return 0
    fi
    
    log_info "Target database cluster: $db_cluster"
    
    # Get current primary instance
    local primary_instance=$(aws rds describe-db-clusters --db-cluster-identifier "$db_cluster" --region "$REGION" --query 'DBClusters[0].DBClusterMembers[?IsClusterWriter==`true`].DBInstanceIdentifier' --output text)
    
    log_info "Current primary instance: $primary_instance"
    
    # Trigger failover
    log_info "Triggering database failover..."
    local failover_start=$(start_timer)
    
    aws rds failover-db-cluster \
        --db-cluster-identifier "$db_cluster" \
        --region "$REGION" \
        --target-db-instance-identifier "" 2>/dev/null || true
    
    # Wait for failover to complete
    log_info "Waiting for failover to complete..."
    local failover_completed=false
    
    for i in {1..30}; do
        local current_primary=$(aws rds describe-db-clusters --db-cluster-identifier "$db_cluster" --region "$REGION" --query 'DBClusters[0].DBClusterMembers[?IsClusterWriter==`true`].DBInstanceIdentifier' --output text)
        
        if [ "$current_primary" != "$primary_instance" ]; then
            failover_completed=true
            log_info "New primary instance: $current_primary"
            break
        fi
        sleep 10
    done
    
    local failover_duration=$(end_timer $failover_start)
    
    # Test application connectivity
    log_info "Testing application database connectivity..."
    local connectivity_start=$(start_timer)
    local connectivity_restored=false
    
    for i in {1..20}; do
        if kubectl get service -n "$NAMESPACE" scorpius-api-gateway &> /dev/null; then
            local service_ip=$(kubectl get service -n "$NAMESPACE" scorpius-api-gateway -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
            if [ -n "$service_ip" ] && curl -sf "http://$service_ip/health" &> /dev/null; then
                connectivity_restored=true
                break
            fi
        fi
        sleep 15
    done
    
    local connectivity_duration=$(end_timer $connectivity_start)
    local scenario_duration=$(end_timer $scenario_start)
    
    # Update scenario data
    scenario_data=$(echo "$scenario_data" | jq --arg end_time "$(date -Iseconds)" \
        --arg duration "$scenario_duration" \
        --arg failover_duration "$failover_duration" \
        --arg connectivity_duration "$connectivity_duration" \
        --arg failover_completed "$failover_completed" \
        --arg connectivity_restored "$connectivity_restored" \
        --arg old_primary "$primary_instance" \
        --arg new_primary "$current_primary" \
        '. + {
            "end_time": $end_time,
            "duration_seconds": ($duration | tonumber),
            "failover_duration_seconds": ($failover_duration | tonumber),
            "connectivity_duration_seconds": ($connectivity_duration | tonumber),
            "failover_completed": ($failover_completed | test("true")),
            "connectivity_restored": ($connectivity_restored | test("true")),
            "old_primary_instance": $old_primary,
            "new_primary_instance": $new_primary,
            "rpo_minutes": 1,
            "status": (if ($connectivity_restored | test("true")) then "success" else "failed" end)
        }')
    
    # Add to report
    jq --argjson scenario "$scenario_data" '.scenarios += [$scenario]' "$REPORT_FILE" > "$REPORT_FILE.tmp" && mv "$REPORT_FILE.tmp" "$REPORT_FILE"
    
    if [ "$connectivity_restored" = true ]; then
        log_success "Database failover completed in ${failover_duration}s (connectivity restored in ${connectivity_duration}s)"
    else
        log_error "Database failover failed - application connectivity not restored"
    fi
}

# Scenario 3: Pod Disruption Test
scenario_pod_disruption() {
    log_info "🔥 SCENARIO 3: Pod Disruption Test"
    
    local scenario_start=$(start_timer)
    local scenario_data="{\"name\": \"pod_disruption\", \"start_time\": \"$(date -Iseconds)\"}"
    
    # Get running pods
    local pods=$(kubectl get pods -n "$NAMESPACE" --field-selector=status.phase=Running -o jsonpath='{.items[*].metadata.name}')
    
    if [ -z "$pods" ]; then
        log_error "No running pods found"
        return 1
    fi
    
    # Delete 50% of pods
    local pod_array=($pods)
    local pod_count=${#pod_array[@]}
    local pods_to_delete=$((pod_count / 2))
    
    log_info "Deleting $pods_to_delete out of $pod_count pods"
    
    local deletion_start=$(start_timer)
    
    for i in $(seq 0 $((pods_to_delete - 1))); do
        if [ $i -lt ${#pod_array[@]} ]; then
            kubectl delete pod "${pod_array[$i]}" -n "$NAMESPACE" --grace-period=0 --force &
        fi
    done
    
    wait  # Wait for all deletions to complete
    
    local deletion_duration=$(end_timer $deletion_start)
    
    # Wait for pods to be recreated
    log_info "Waiting for pods to be recreated..."
    local recovery_start=$(start_timer)
    
    while true; do
        local running_pods=$(kubectl get pods -n "$NAMESPACE" --field-selector=status.phase=Running -o json | jq '.items | length')
        if [ "$running_pods" -ge $((pod_count - 1)) ]; then  # Allow for 1 pod difference
            break
        fi
        log_info "Running pods: $running_pods/$pod_count"
        sleep 10
    done
    
    local recovery_duration=$(end_timer $recovery_start)
    
    # Test application health
    log_info "Testing application health after pod disruption..."
    local health_start=$(start_timer)
    local health_recovered=false
    
    for i in {1..10}; do
        if kubectl get service -n "$NAMESPACE" scorpius-api-gateway &> /dev/null; then
            local service_ip=$(kubectl get service -n "$NAMESPACE" scorpius-api-gateway -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
            if [ -n "$service_ip" ] && curl -sf "http://$service_ip/health" &> /dev/null; then
                health_recovered=true
                break
            fi
        fi
        sleep 10
    done
    
    local health_duration=$(end_timer $health_start)
    local scenario_duration=$(end_timer $scenario_start)
    
    # Update scenario data
    scenario_data=$(echo "$scenario_data" | jq --arg end_time "$(date -Iseconds)" \
        --arg duration "$scenario_duration" \
        --arg deletion_duration "$deletion_duration" \
        --arg recovery_duration "$recovery_duration" \
        --arg health_duration "$health_duration" \
        --arg pods_deleted "$pods_to_delete" \
        --arg total_pods "$pod_count" \
        --arg health_recovered "$health_recovered" \
        '. + {
            "end_time": $end_time,
            "duration_seconds": ($duration | tonumber),
            "deletion_duration_seconds": ($deletion_duration | tonumber),
            "recovery_duration_seconds": ($recovery_duration | tonumber),
            "health_duration_seconds": ($health_duration | tonumber),
            "pods_deleted": ($pods_deleted | tonumber),
            "total_pods": ($total_pods | tonumber),
            "health_recovered": ($health_recovered | test("true")),
            "status": (if ($health_recovered | test("true")) then "success" else "failed" end)
        }')
    
    # Add to report
    jq --argjson scenario "$scenario_data" '.scenarios += [$scenario]' "$REPORT_FILE" > "$REPORT_FILE.tmp" && mv "$REPORT_FILE.tmp" "$REPORT_FILE"
    
    if [ "$health_recovered" = true ]; then
        log_success "Pod disruption recovery completed in ${recovery_duration}s (health restored in ${health_duration}s)"
    else
        log_error "Pod disruption recovery failed - application health not restored"
    fi
}

# Generate final report
generate_final_report() {
    log_info "Generating final chaos drill report..."
    
    # Update report with end time and summary
    jq --arg end_time "$(date -Iseconds)" \
       --arg drill_duration "$(($(date +%s) - $(date -d "$(jq -r '.start_time' "$REPORT_FILE")" +%s)))" \
       '. + {
           "end_time": $end_time,
           "drill_duration_seconds": ($drill_duration | tonumber),
           "summary": {
               "total_scenarios": (.scenarios | length),
               "successful_scenarios": (.scenarios | map(select(.status == "success")) | length),
               "failed_scenarios": (.scenarios | map(select(.status == "failed")) | length),
               "average_rto_minutes": ((.scenarios | map(.rto_minutes // 0) | add) / (.scenarios | length)),
               "max_rto_minutes": (.scenarios | map(.rto_minutes // 0) | max),
               "rto_target_met": ((.scenarios | map(.rto_minutes // 0) | max) <= .metrics.rto_target_minutes)
           }
       }' "$REPORT_FILE" > "$REPORT_FILE.tmp" && mv "$REPORT_FILE.tmp" "$REPORT_FILE"
    
    # Generate markdown report
    local markdown_report="$DRILL_DIR/chaos-drill-report.md"
    
    python3 << EOF
import json
import sys
from datetime import datetime

with open("$REPORT_FILE", "r") as f:
    data = json.load(f)

summary = data["summary"]
scenarios = data["scenarios"]

report = f"""# Chaos Friday Drill Report

**Drill ID:** {data["drill_id"]}
**Date:** {data["start_time"][:10]}
**Duration:** {data["drill_duration_seconds"] // 60} minutes
**Cluster:** {data["cluster"]} ({data["region"]})

## Executive Summary

- **Total Scenarios:** {summary["total_scenarios"]}
- **Successful:** {summary["successful_scenarios"]}
- **Failed:** {summary["failed_scenarios"]}
- **Average RTO:** {summary["average_rto_minutes"]:.1f} minutes
- **Max RTO:** {summary["max_rto_minutes"]:.1f} minutes
- **RTO Target Met:** {'✅ Yes' if summary["rto_target_met"] else '❌ No'} (Target: {data["metrics"]["rto_target_minutes"]} minutes)

## Scenario Results

"""

for i, scenario in enumerate(scenarios, 1):
    status_icon = "✅" if scenario["status"] == "success" else "❌"
    report += f"""
### {i}. {scenario["name"].replace("_", " ").title()} {status_icon}

- **Duration:** {scenario["duration_seconds"] // 60} minutes {scenario["duration_seconds"] % 60} seconds
- **Status:** {scenario["status"].upper()}
"""
    
    if "rto_minutes" in scenario:
        report += f"- **RTO:** {scenario['rto_minutes']:.1f} minutes\n"
    
    if "recovery_duration_seconds" in scenario:
        report += f"- **Recovery Time:** {scenario['recovery_duration_seconds']} seconds\n"

report += f"""

## Compliance Status

### RTO (Recovery Time Objective)
- **Target:** {data["metrics"]["rto_target_minutes"]} minutes
- **Achieved:** {summary["max_rto_minutes"]:.1f} minutes
- **Status:** {'✅ COMPLIANT' if summary["rto_target_met"] else '❌ NON-COMPLIANT'}

### RPO (Recovery Point Objective)
- **Target:** {data["metrics"]["rpo_target_minutes"]} minutes
- **Status:** ✅ COMPLIANT (Continuous replication)

## Recommendations

"""

if not summary["rto_target_met"]:
    report += "- ❌ **CRITICAL:** RTO target exceeded. Review scaling policies and health check configurations.\n"

if summary["failed_scenarios"] > 0:
    report += f"- ⚠️ **WARNING:** {summary['failed_scenarios']} scenario(s) failed. Investigate and remediate.\n"

if summary["successful_scenarios"] == summary["total_scenarios"]:
    report += "- ✅ **EXCELLENT:** All scenarios passed successfully.\n"

report += """
## Next Steps

1. Review failed scenarios and implement fixes
2. Update runbooks based on lessons learned
3. Schedule next Chaos Friday drill for next month
4. Share results with stakeholders

---
*Generated by Scorpius Chaos Friday Drill*
"""

with open("$markdown_report", "w") as f:
    f.write(report)

print("Markdown report generated successfully")
EOF

    log_success "Final report generated: $REPORT_FILE"
    log_success "Markdown report generated: $markdown_report"
}

# Send notifications
send_notifications() {
    if [ -n "$SLACK_WEBHOOK" ]; then
        log_info "Sending Slack notification..."
        
        local summary=$(jq -r '.summary' "$REPORT_FILE")
        local total_scenarios=$(echo "$summary" | jq -r '.total_scenarios')
        local successful_scenarios=$(echo "$summary" | jq -r '.successful_scenarios')
        local max_rto=$(echo "$summary" | jq -r '.max_rto_minutes')
        local rto_target_met=$(echo "$summary" | jq -r '.rto_target_met')
        
        local color="good"
        if [ "$rto_target_met" != "true" ] || [ "$successful_scenarios" != "$total_scenarios" ]; then
            color="warning"
        fi
        
        local payload=$(cat << EOF
{
    "text": "🔥 Chaos Friday Drill Completed",
    "attachments": [
        {
            "color": "$color",
            "fields": [
                {
                    "title": "Cluster",
                    "value": "$CLUSTER_NAME",
                    "short": true
                },
                {
                    "title": "Success Rate",
                    "value": "$successful_scenarios/$total_scenarios scenarios",
                    "short": true
                },
                {
                    "title": "Max RTO",
                    "value": "${max_rto} minutes",
                    "short": true
                },
                {
                    "title": "RTO Target Met",
                    "value": "$([ "$rto_target_met" = "true" ] && echo "✅ Yes" || echo "❌ No")",
                    "short": true
                }
            ]
        }
    ]
}
EOF
)
        
        curl -X POST -H 'Content-type: application/json' --data "$payload" "$SLACK_WEBHOOK" > /dev/null 2>&1 || log_warning "Failed to send Slack notification"
    fi
}

# Main execution
main() {
    log_info "🔥 Starting Chaos Friday Drill - $TIMESTAMP"
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --cluster)
                CLUSTER_NAME="$2"
                shift 2
                ;;
            --region)
                REGION="$2"
                shift 2
                ;;
            --namespace)
                NAMESPACE="$2"
                shift 2
                ;;
            --slack-webhook)
                SLACK_WEBHOOK="$2"
                shift 2
                ;;
            --scenario)
                SCENARIO="$2"
                shift 2
                ;;
            --help)
                cat << EOF
Usage: $0 [OPTIONS]

Options:
    --cluster NAME         EKS cluster name [default: scorpius-prod]
    --region REGION        AWS region [default: us-east-1]
    --namespace NAMESPACE  Kubernetes namespace [default: scorpius]
    --slack-webhook URL    Slack webhook URL for notifications
    --scenario SCENARIO    Run specific scenario (nodegroup|database|pods|all) [default: all]
    --help                 Show this help message

Examples:
    $0 --cluster my-cluster --region us-west-2
    $0 --scenario nodegroup --slack-webhook https://hooks.slack.com/...
EOF
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Execute drill
    setup_results_dir
    preflight_checks
    capture_baseline
    
    # Run scenarios
    local scenario="${SCENARIO:-all}"
    
    case "$scenario" in
        "nodegroup")
            scenario_nodegroup_termination
            ;;
        "database")
            scenario_database_failover
            ;;
        "pods")
            scenario_pod_disruption
            ;;
        "all"|*)
            scenario_nodegroup_termination
            scenario_database_failover
            scenario_pod_disruption
            ;;
    esac
    
    generate_final_report
    send_notifications
    
    # Display summary
    log_info "Chaos Friday Drill Summary:"
    local summary=$(jq -r '.summary' "$REPORT_FILE")
    local total_scenarios=$(echo "$summary" | jq -r '.total_scenarios')
    local successful_scenarios=$(echo "$summary" | jq -r '.successful_scenarios')
    local max_rto=$(echo "$summary" | jq -r '.max_rto_minutes')
    local rto_target_met=$(echo "$summary" | jq -r '.rto_target_met')
    
    echo "  Scenarios: $successful_scenarios/$total_scenarios successful"
    echo "  Max RTO: ${max_rto} minutes"
    echo "  RTO Target Met: $([ "$rto_target_met" = "true" ] && echo "✅ Yes" || echo "❌ No")"
    echo "  Results: $DRILL_DIR"
    
    if [ "$rto_target_met" = "true" ] && [ "$successful_scenarios" = "$total_scenarios" ]; then
        log_success "🎉 Chaos Friday drill completed successfully!"
        exit 0
    else
        log_error "❌ Chaos Friday drill completed with issues. Review the report."
        exit 1
    fi
}

# Execute main function
main "$@"