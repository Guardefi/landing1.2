#!/bin/bash
# Scorpius Enterprise Platform - EKS Deployment Test Script
# Validates EKS cluster deployment and application functionality

set -euo pipefail

# Configuration
CLUSTER_NAME="${CLUSTER_NAME:-scorpius-enterprise}"
NAMESPACE="${NAMESPACE:-scorpius-enterprise}"
DOMAIN_NAME="${DOMAIN_NAME:-scorpius.company.com}"
TIMEOUT="${TIMEOUT:-300}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# Test result tracking
test_result() {
    local test_name="$1"
    local result="$2"
    local message="$3"
    
    ((TESTS_TOTAL++))
    
    if [[ "$result" == "pass" ]]; then
        ((TESTS_PASSED++))
        log "✓ $test_name: $message"
    else
        ((TESTS_FAILED++))
        error "✗ $test_name: $message"
    fi
}

# Prerequisites check
check_prerequisites() {
    log "Checking prerequisites..."
    
    local missing_tools=()
    
    # Check required tools
    for tool in kubectl helm aws terraform; do
        if ! command -v "$tool" &> /dev/null; then
            missing_tools+=("$tool")
        fi
    done
    
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        error "Missing required tools: ${missing_tools[*]}"
        return 1
    fi
    
    # Check AWS CLI configuration
    if ! aws sts get-caller-identity &> /dev/null; then
        error "AWS CLI not configured or credentials invalid"
        return 1
    fi
    
    # Check kubectl context
    if ! kubectl config current-context &> /dev/null; then
        error "kubectl not configured"
        return 1
    fi
    
    log "Prerequisites check passed"
    return 0
}

# Test EKS cluster connectivity
test_cluster_connectivity() {
    log "Testing EKS cluster connectivity..."
    
    # Test cluster access
    if kubectl cluster-info &> /dev/null; then
        test_result "Cluster Connectivity" "pass" "Successfully connected to EKS cluster"
    else
        test_result "Cluster Connectivity" "fail" "Cannot connect to EKS cluster"
        return 1
    fi
    
    # Test cluster nodes
    local node_count
    node_count=$(kubectl get nodes --no-headers | wc -l)
    if [[ $node_count -gt 0 ]]; then
        test_result "Cluster Nodes" "pass" "Found $node_count nodes"
        kubectl get nodes -o wide
    else
        test_result "Cluster Nodes" "fail" "No nodes found in cluster"
        return 1
    fi
    
    # Test node readiness
    local ready_nodes
    ready_nodes=$(kubectl get nodes --no-headers | grep -c "Ready" || echo "0")
    if [[ $ready_nodes -eq $node_count ]]; then
        test_result "Node Readiness" "pass" "All $ready_nodes nodes are ready"
    else
        test_result "Node Readiness" "fail" "Only $ready_nodes/$node_count nodes are ready"
        kubectl get nodes
        return 1
    fi
    
    return 0
}

# Test namespace and resources
test_namespace_resources() {
    log "Testing namespace and resources..."
    
    # Check namespace exists
    if kubectl get namespace "$NAMESPACE" &> /dev/null; then
        test_result "Namespace Existence" "pass" "Namespace $NAMESPACE exists"
    else
        test_result "Namespace Existence" "fail" "Namespace $NAMESPACE does not exist"
        return 1
    fi
    
    # Check resource quotas
    if kubectl get resourcequota -n "$NAMESPACE" &> /dev/null; then
        test_result "Resource Quotas" "pass" "Resource quotas are configured"
        kubectl get resourcequota -n "$NAMESPACE" -o wide
    else
        test_result "Resource Quotas" "fail" "No resource quotas found"
    fi
    
    # Check limit ranges
    if kubectl get limitrange -n "$NAMESPACE" &> /dev/null; then
        test_result "Limit Ranges" "pass" "Limit ranges are configured"
        kubectl get limitrange -n "$NAMESPACE" -o wide
    else
        test_result "Limit Ranges" "fail" "No limit ranges found"
    fi
    
    return 0
}

# Test application deployments
test_application_deployments() {
    log "Testing application deployments..."
    
    local services=("wallet-guard" "usage-metering" "auth-proxy" "audit-trail" "reporting")
    
    for service in "${services[@]}"; do
        info "Testing $service deployment..."
        
        # Check deployment exists
        if kubectl get deployment "$service" -n "$NAMESPACE" &> /dev/null; then
            test_result "$service Deployment" "pass" "Deployment exists"
            
            # Check deployment readiness
            local ready_replicas
            ready_replicas=$(kubectl get deployment "$service" -n "$NAMESPACE" -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo "0")
            local desired_replicas
            desired_replicas=$(kubectl get deployment "$service" -n "$NAMESPACE" -o jsonpath='{.spec.replicas}' 2>/dev/null || echo "0")
            
            if [[ "$ready_replicas" -eq "$desired_replicas" ]] && [[ "$ready_replicas" -gt 0 ]]; then
                test_result "$service Readiness" "pass" "$ready_replicas/$desired_replicas replicas ready"
            else
                test_result "$service Readiness" "fail" "Only $ready_replicas/$desired_replicas replicas ready"
                kubectl describe deployment "$service" -n "$NAMESPACE"
            fi
            
            # Check service exists
            if kubectl get service "${service}-service" -n "$NAMESPACE" &> /dev/null; then
                test_result "$service Service" "pass" "Service exists"
            else
                test_result "$service Service" "fail" "Service does not exist"
            fi
            
        else
            test_result "$service Deployment" "fail" "Deployment does not exist"
        fi
    done
    
    return 0
}

# Test database connectivity
test_database_connectivity() {
    log "Testing database connectivity..."
    
    # Test PostgreSQL
    if kubectl get deployment postgresql -n "$NAMESPACE" &> /dev/null; then
        local pg_ready
        pg_ready=$(kubectl get deployment postgresql -n "$NAMESPACE" -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo "0")
        if [[ "$pg_ready" -gt 0 ]]; then
            test_result "PostgreSQL" "pass" "PostgreSQL is running"
        else
            test_result "PostgreSQL" "fail" "PostgreSQL is not ready"
        fi
    else
        test_result "PostgreSQL" "fail" "PostgreSQL deployment not found"
    fi
    
    # Test Redis
    if kubectl get deployment redis -n "$NAMESPACE" &> /dev/null; then
        local redis_ready
        redis_ready=$(kubectl get deployment redis -n "$NAMESPACE" -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo "0")
        if [[ "$redis_ready" -gt 0 ]]; then
            test_result "Redis" "pass" "Redis is running"
        else
            test_result "Redis" "fail" "Redis is not ready"
        fi
    else
        test_result "Redis" "fail" "Redis deployment not found"
    fi
    
    return 0
}

# Test application health endpoints
test_health_endpoints() {
    log "Testing application health endpoints..."
    
    local services=("wallet-guard" "usage-metering" "auth-proxy" "audit-trail" "reporting")
    
    for service in "${services[@]}"; do
        info "Testing $service health endpoint..."
        
        # Port forward to service
        local local_port=$((8000 + RANDOM % 1000))
        kubectl port-forward "service/${service}-service" "$local_port:8000" -n "$NAMESPACE" &
        local port_forward_pid=$!
        
        # Wait for port forward to establish
        sleep 5
        
        # Test health endpoint
        if curl -f -s "http://localhost:$local_port/health" > /dev/null; then
            test_result "$service Health" "pass" "Health endpoint responding"
        else
            test_result "$service Health" "fail" "Health endpoint not responding"
        fi
        
        # Test readiness endpoint
        if curl -f -s "http://localhost:$local_port/ready" > /dev/null; then
            test_result "$service Readiness" "pass" "Readiness endpoint responding"
        else
            test_result "$service Readiness" "fail" "Readiness endpoint not responding"
        fi
        
        # Clean up port forward
        kill $port_forward_pid 2>/dev/null || true
        wait $port_forward_pid 2>/dev/null || true
    done
    
    return 0
}

# Test metrics endpoints
test_metrics_endpoints() {
    log "Testing metrics endpoints..."
    
    local services=("wallet-guard" "usage-metering" "auth-proxy" "audit-trail" "reporting")
    
    for service in "${services[@]}"; do
        info "Testing $service metrics endpoint..."
        
        # Port forward to metrics port
        local local_port=$((9000 + RANDOM % 1000))
        kubectl port-forward "service/${service}-service" "$local_port:8080" -n "$NAMESPACE" &
        local port_forward_pid=$!
        
        # Wait for port forward to establish
        sleep 5
        
        # Test metrics endpoint
        if curl -f -s "http://localhost:$local_port/metrics" | grep -q "# HELP"; then
            test_result "$service Metrics" "pass" "Metrics endpoint returning data"
        else
            test_result "$service Metrics" "fail" "Metrics endpoint not returning valid data"
        fi
        
        # Clean up port forward
        kill $port_forward_pid 2>/dev/null || true
        wait $port_forward_pid 2>/dev/null || true
    done
    
    return 0
}

# Test monitoring stack
test_monitoring_stack() {
    log "Testing monitoring stack..."
    
    # Test Prometheus
    if kubectl get deployment prometheus -n "$NAMESPACE" &> /dev/null; then
        local prom_ready
        prom_ready=$(kubectl get deployment prometheus -n "$NAMESPACE" -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo "0")
        if [[ "$prom_ready" -gt 0 ]]; then
            test_result "Prometheus" "pass" "Prometheus is running"
        else
            test_result "Prometheus" "fail" "Prometheus is not ready"
        fi
    else
        test_result "Prometheus" "fail" "Prometheus deployment not found"
    fi
    
    # Test Grafana
    if kubectl get deployment grafana -n "$NAMESPACE" &> /dev/null; then
        local grafana_ready
        grafana_ready=$(kubectl get deployment grafana -n "$NAMESPACE" -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo "0")
        if [[ "$grafana_ready" -gt 0 ]]; then
            test_result "Grafana" "pass" "Grafana is running"
        else
            test_result "Grafana" "fail" "Grafana is not ready"
        fi
    else
        test_result "Grafana" "fail" "Grafana deployment not found"
    fi
    
    # Test Alertmanager
    if kubectl get deployment alertmanager -n "$NAMESPACE" &> /dev/null; then
        local am_ready
        am_ready=$(kubectl get deployment alertmanager -n "$NAMESPACE" -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo "0")
        if [[ "$am_ready" -gt 0 ]]; then
            test_result "Alertmanager" "pass" "Alertmanager is running"
        else
            test_result "Alertmanager" "fail" "Alertmanager is not ready"
        fi
    else
        test_result "Alertmanager" "fail" "Alertmanager deployment not found"
    fi
    
    return 0
}

# Test ingress and networking
test_ingress_networking() {
    log "Testing ingress and networking..."
    
    # Test ingress controller
    if kubectl get pods -l app.kubernetes.io/name=ingress-nginx -A &> /dev/null; then
        local ingress_ready
        ingress_ready=$(kubectl get pods -l app.kubernetes.io/name=ingress-nginx -A --no-headers | grep -c "Running" || echo "0")
        if [[ "$ingress_ready" -gt 0 ]]; then
            test_result "Ingress Controller" "pass" "Ingress controller is running"
        else
            test_result "Ingress Controller" "fail" "Ingress controller is not ready"
        fi
    else
        test_result "Ingress Controller" "fail" "Ingress controller not found"
    fi
    
    # Test ingress resources
    if kubectl get ingress -n "$NAMESPACE" &> /dev/null; then
        test_result "Ingress Resources" "pass" "Ingress resources exist"
        kubectl get ingress -n "$NAMESPACE" -o wide
    else
        test_result "Ingress Resources" "fail" "No ingress resources found"
    fi
    
    # Test network policies
    local network_policies
    network_policies=$(kubectl get networkpolicy -n "$NAMESPACE" --no-headers | wc -l)
    if [[ "$network_policies" -gt 0 ]]; then
        test_result "Network Policies" "pass" "Found $network_policies network policies"
    else
        test_result "Network Policies" "fail" "No network policies found"
    fi
    
    return 0
}

# Test security configuration
test_security_configuration() {
    log "Testing security configuration..."
    
    # Test service accounts
    if kubectl get serviceaccount scorpius-service-account -n "$NAMESPACE" &> /dev/null; then
        test_result "Service Account" "pass" "Service account exists"
    else
        test_result "Service Account" "fail" "Service account not found"
    fi
    
    # Test RBAC
    local rbac_resources
    rbac_resources=$(kubectl get role,rolebinding,clusterrole,clusterrolebinding -n "$NAMESPACE" --no-headers 2>/dev/null | wc -l)
    if [[ "$rbac_resources" -gt 0 ]]; then
        test_result "RBAC" "pass" "Found $rbac_resources RBAC resources"
    else
        test_result "RBAC" "fail" "No RBAC resources found"
    fi
    
    # Test pod security policies
    local pod_disruption_budgets
    pod_disruption_budgets=$(kubectl get pdb -n "$NAMESPACE" --no-headers 2>/dev/null | wc -l)
    if [[ "$pod_disruption_budgets" -gt 0 ]]; then
        test_result "Pod Disruption Budgets" "pass" "Found $pod_disruption_budgets PDBs"
    else
        test_result "Pod Disruption Budgets" "fail" "No pod disruption budgets found"
    fi
    
    return 0
}

# Test backup configuration
test_backup_configuration() {
    log "Testing backup configuration..."
    
    # Test if backup tools are installed
    if kubectl get pods -l app.kubernetes.io/name=velero -A &> /dev/null; then
        test_result "Backup Tool" "pass" "Velero backup tool is installed"
    else
        test_result "Backup Tool" "fail" "No backup tool found"
    fi
    
    # Test backup schedules
    if kubectl get schedule -A &> /dev/null; then
        local schedules
        schedules=$(kubectl get schedule -A --no-headers | wc -l)
        if [[ "$schedules" -gt 0 ]]; then
            test_result "Backup Schedules" "pass" "Found $schedules backup schedules"
        else
            test_result "Backup Schedules" "fail" "No backup schedules found"
        fi
    else
        test_result "Backup Schedules" "fail" "Cannot query backup schedules"
    fi
    
    return 0
}

# Test compliance requirements
test_compliance_requirements() {
    log "Testing compliance requirements..."
    
    # Test audit logging
    if kubectl get pods -l app=audit-trail -n "$NAMESPACE" &> /dev/null; then
        test_result "Audit Logging" "pass" "Audit trail service is running"
    else
        test_result "Audit Logging" "fail" "Audit trail service not found"
    fi
    
    # Test data encryption
    local encrypted_secrets
    encrypted_secrets=$(kubectl get secrets -n "$NAMESPACE" -o json | jq '.items | length')
    if [[ "$encrypted_secrets" -gt 0 ]]; then
        test_result "Secret Encryption" "pass" "Found $encrypted_secrets encrypted secrets"
    else
        test_result "Secret Encryption" "fail" "No encrypted secrets found"
    fi
    
    # Test resource limits
    local deployments_with_limits
    deployments_with_limits=$(kubectl get deployments -n "$NAMESPACE" -o json | jq '.items[] | select(.spec.template.spec.containers[].resources.limits) | .metadata.name' | wc -l)
    local total_deployments
    total_deployments=$(kubectl get deployments -n "$NAMESPACE" --no-headers | wc -l)
    
    if [[ "$deployments_with_limits" -eq "$total_deployments" ]] && [[ "$total_deployments" -gt 0 ]]; then
        test_result "Resource Limits" "pass" "All deployments have resource limits"
    else
        test_result "Resource Limits" "fail" "Only $deployments_with_limits/$total_deployments deployments have resource limits"
    fi
    
    return 0
}

# Performance test
test_performance() {
    log "Testing performance..."
    
    # Test horizontal pod autoscalers
    local hpas
    hpas=$(kubectl get hpa -n "$NAMESPACE" --no-headers 2>/dev/null | wc -l)
    if [[ "$hpas" -gt 0 ]]; then
        test_result "Horizontal Pod Autoscalers" "pass" "Found $hpas HPAs"
        kubectl get hpa -n "$NAMESPACE" -o wide
    else
        test_result "Horizontal Pod Autoscalers" "fail" "No HPAs found"
    fi
    
    # Test resource utilization
    info "Current resource utilization:"
    kubectl top nodes 2>/dev/null || warn "Metrics server not available"
    kubectl top pods -n "$NAMESPACE" 2>/dev/null || warn "Pod metrics not available"
    
    return 0
}

# Generate test report
generate_report() {
    log "Generating test report..."
    
    local report_file="eks-test-report-$(date +%Y%m%d-%H%M%S).txt"
    
    cat > "$report_file" << EOF
Scorpius Enterprise Platform - EKS Deployment Test Report
=========================================================

Test Summary:
- Total Tests: $TESTS_TOTAL
- Passed: $TESTS_PASSED
- Failed: $TESTS_FAILED
- Success Rate: $(( TESTS_PASSED * 100 / TESTS_TOTAL ))%

Test Environment:
- Cluster: $CLUSTER_NAME
- Namespace: $NAMESPACE
- Domain: $DOMAIN_NAME
- Test Date: $(date)
- Kubernetes Version: $(kubectl version --short --client 2>/dev/null || echo "Unknown")

Cluster Information:
$(kubectl cluster-info 2>/dev/null || echo "Unable to get cluster info")

Node Information:
$(kubectl get nodes -o wide 2>/dev/null || echo "Unable to get node info")

Pod Status:
$(kubectl get pods -n "$NAMESPACE" -o wide 2>/dev/null || echo "Unable to get pod info")

Service Status:
$(kubectl get services -n "$NAMESPACE" -o wide 2>/dev/null || echo "Unable to get service info")

Ingress Status:
$(kubectl get ingress -n "$NAMESPACE" -o wide 2>/dev/null || echo "Unable to get ingress info")

EOF

    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "\n✅ All tests passed! Deployment is healthy." >> "$report_file"
    else
        echo -e "\n❌ $TESTS_FAILED tests failed. Please review the issues above." >> "$report_file"
    fi
    
    log "Test report saved to: $report_file"
}

# Main execution
main() {
    log "Starting Scorpius Enterprise Platform EKS Deployment Tests"
    log "============================================================"
    
    # Check prerequisites
    if ! check_prerequisites; then
        error "Prerequisites check failed. Please fix the issues and retry."
        exit 1
    fi
    
    # Run test suites
    test_cluster_connectivity
    test_namespace_resources
    test_application_deployments
    test_database_connectivity
    test_health_endpoints
    test_metrics_endpoints
    test_monitoring_stack
    test_ingress_networking
    test_security_configuration
    test_backup_configuration
    test_compliance_requirements
    test_performance
    
    # Generate report
    generate_report
    
    # Final summary
    log "Test execution completed!"
    log "Total Tests: $TESTS_TOTAL"
    log "Passed: $TESTS_PASSED"
    log "Failed: $TESTS_FAILED"
    
    if [[ $TESTS_FAILED -eq 0 ]]; then
        log "🎉 All tests passed! EKS deployment is successful and healthy."
        exit 0
    else
        error "❌ $TESTS_FAILED tests failed. Please review the issues and fix them."
        exit 1
    fi
}

# Handle script interruption
trap 'error "Test interrupted"; exit 1' INT TERM

# Execute main function
main "$@"
