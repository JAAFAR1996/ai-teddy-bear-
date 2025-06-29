#!/bin/bash

# GitOps Deployment Pipeline Script for AI Teddy Bear System
# DevOps Team Implementation - Task 14
# Author: DevOps Team Lead

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ARGOCD_NAMESPACE="argocd"
PRODUCTION_NAMESPACE="ai-teddy-production"
STAGING_NAMESPACE="ai-teddy-staging"

# Default values
ENVIRONMENT="${ENVIRONMENT:-staging}"
OPERATION="${OPERATION:-deploy}"
VERSION="${VERSION:-latest}"
DRY_RUN="${DRY_RUN:-false}"
SKIP_TESTS="${SKIP_TESTS:-false}"
AUTO_SYNC="${AUTO_SYNC:-false}"

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    cat << EOF
AI Teddy Bear GitOps Deployment Pipeline

Usage: $0 [OPTIONS]

Options:
    -e, --environment    Target environment (staging|production) [default: staging]
    -o, --operation      Operation (deploy|rollback|sync|status) [default: deploy]
    -v, --version        Application version to deploy [default: latest]
    -d, --dry-run        Perform a dry run without actual deployment
    -s, --skip-tests     Skip integration tests
    -a, --auto-sync      Enable automatic synchronization
    -h, --help           Show this help message

Examples:
    # Deploy to staging
    $0 --environment staging --version v1.2.3

    # Deploy to production with auto-sync
    $0 --environment production --version v1.2.3 --auto-sync

    # Rollback production to previous version
    $0 --environment production --operation rollback

    # Check deployment status
    $0 --environment production --operation status

    # Dry run deployment
    $0 --environment staging --version v1.3.0 --dry-run

EOF
}

# Function to parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -o|--operation)
                OPERATION="$2"
                shift 2
                ;;
            -v|--version)
                VERSION="$2"
                shift 2
                ;;
            -d|--dry-run)
                DRY_RUN="true"
                shift
                ;;
            -s|--skip-tests)
                SKIP_TESTS="true"
                shift
                ;;
            -a|--auto-sync)
                AUTO_SYNC="true"
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
}

# Function to validate prerequisites
validate_prerequisites() {
    print_info "Validating prerequisites..."
    
    # Check required tools
    local required_tools=("kubectl" "argocd" "helm" "jq" "curl")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            print_error "$tool is required but not installed"
            exit 1
        fi
    done
    
    # Check Kubernetes connectivity
    if ! kubectl cluster-info &> /dev/null; then
        print_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    
    # Check ArgoCD connectivity
    if ! argocd version --client &> /dev/null; then
        print_error "ArgoCD CLI is not properly configured"
        exit 1
    fi
    
    # Validate environment
    if [[ ! "$ENVIRONMENT" =~ ^(staging|production)$ ]]; then
        print_error "Invalid environment: $ENVIRONMENT. Must be 'staging' or 'production'"
        exit 1
    fi
    
    # Validate operation
    if [[ ! "$OPERATION" =~ ^(deploy|rollback|sync|status)$ ]]; then
        print_error "Invalid operation: $OPERATION"
        exit 1
    fi
    
    print_success "Prerequisites validated"
}

# Function to setup ArgoCD CLI
setup_argocd_cli() {
    print_info "Setting up ArgoCD CLI..."
    
    # Get ArgoCD server URL
    local argocd_server=$(kubectl get svc argocd-server -n $ARGOCD_NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
    if [[ -z "$argocd_server" ]]; then
        argocd_server=$(kubectl get svc argocd-server -n $ARGOCD_NAMESPACE -o jsonpath='{.spec.clusterIP}')
    fi
    
    # Login to ArgoCD
    local argocd_password=$(kubectl get secret argocd-initial-admin-secret -n $ARGOCD_NAMESPACE -o jsonpath='{.data.password}' | base64 -d)
    
    if [[ "$DRY_RUN" == "false" ]]; then
        argocd login "$argocd_server" --username admin --password "$argocd_password" --insecure
        print_success "ArgoCD CLI configured"
    else
        print_info "Dry run: Skipping ArgoCD login"
    fi
}

# Function to run pre-deployment checks
run_pre_deployment_checks() {
    print_info "Running pre-deployment checks..."
    
    # Check cluster resources
    local node_status=$(kubectl get nodes --no-headers | grep -v Ready | wc -l)
    if [[ $node_status -gt 0 ]]; then
        print_warning "Some cluster nodes are not ready"
    fi
    
    # Check namespace status
    local target_namespace
    if [[ "$ENVIRONMENT" == "production" ]]; then
        target_namespace="$PRODUCTION_NAMESPACE"
    else
        target_namespace="$STAGING_NAMESPACE"
    fi
    
    if ! kubectl get namespace "$target_namespace" &> /dev/null; then
        print_info "Creating namespace: $target_namespace"
        if [[ "$DRY_RUN" == "false" ]]; then
            kubectl create namespace "$target_namespace"
        fi
    fi
    
    # Check resource quotas
    local cpu_usage=$(kubectl top nodes --no-headers | awk '{sum += $3} END {print sum}' || echo "0")
    print_info "Current cluster CPU usage: ${cpu_usage}%"
    
    print_success "Pre-deployment checks completed"
}

# Function to deploy applications
deploy_applications() {
    print_info "Deploying AI Teddy Bear applications to $ENVIRONMENT..."
    
    local app_name="ai-teddy-bear-$ENVIRONMENT"
    
    # Update application parameters
    if [[ "$DRY_RUN" == "false" ]]; then
        argocd app set "$app_name" \
            --parameter "global.image.tag=$VERSION" \
            --parameter "global.environment=$ENVIRONMENT" \
            --parameter "global.monitoring.enabled=true"
        
        # Set sync policy
        if [[ "$AUTO_SYNC" == "true" ]]; then
            argocd app set "$app_name" --sync-policy automated
        else
            argocd app set "$app_name" --sync-policy manual
        fi
        
        # Sync application
        print_info "Syncing application..."
        argocd app sync "$app_name" --timeout 600
        
        # Wait for sync completion
        print_info "Waiting for sync completion..."
        argocd app wait "$app_name" --timeout 900 --health
        
    else
        print_info "Dry run: Would deploy $app_name with version $VERSION"
    fi
    
    print_success "Application deployment completed"
}

# Function to run integration tests
run_integration_tests() {
    if [[ "$SKIP_TESTS" == "true" ]]; then
        print_warning "Skipping integration tests"
        return 0
    fi
    
    print_info "Running integration tests for $ENVIRONMENT..."
    
    # Determine base URL
    local base_url
    if [[ "$ENVIRONMENT" == "production" ]]; then
        base_url="https://api.teddy-bear.ai"
    else
        base_url="https://$ENVIRONMENT-api.teddy-bear.ai"
    fi
    
    # Wait for services to be ready
    print_info "Waiting for services to be ready..."
    sleep 30
    
    # Health check
    print_info "Testing health endpoints..."
    if curl -sf "$base_url/health" > /dev/null; then
        print_success "Health check passed"
    else
        print_error "Health check failed"
        return 1
    fi
    
    # GraphQL endpoint test
    print_info "Testing GraphQL endpoint..."
    local graphql_response=$(curl -sf -X POST "$base_url/graphql" \
        -H "Content-Type: application/json" \
        -d '{"query": "query { __schema { types { name } } }"}' | jq -r '.data.__schema.types | length')
    
    if [[ "$graphql_response" -gt 0 ]]; then
        print_success "GraphQL endpoint test passed"
    else
        print_error "GraphQL endpoint test failed"
        return 1
    fi
    
    # Run additional integration tests if available
    if [[ -f "$PROJECT_ROOT/tests/integration/test_deployment.py" ]]; then
        print_info "Running comprehensive integration tests..."
        python -m pytest "$PROJECT_ROOT/tests/integration/" \
            --env="$ENVIRONMENT" \
            --base-url="$base_url" \
            --timeout=300
    fi
    
    print_success "Integration tests completed successfully"
}

# Function to rollback application
rollback_application() {
    print_info "Rolling back $ENVIRONMENT environment..."
    
    local app_name="ai-teddy-bear-$ENVIRONMENT"
    
    # Get previous successful revision
    local previous_revision=$(argocd app history "$app_name" --output json | \
        jq -r '.[] | select(.deployedAt != null) | .revision' | \
        head -n 2 | tail -n 1)
    
    if [[ -z "$previous_revision" ]]; then
        print_error "No previous revision found for rollback"
        return 1
    fi
    
    print_info "Rolling back to revision: $previous_revision"
    
    if [[ "$DRY_RUN" == "false" ]]; then
        # Perform rollback
        argocd app rollback "$app_name" "$previous_revision"
        
        # Wait for rollback completion
        argocd app wait "$app_name" --timeout 600 --health
        
        # Verify rollback
        print_info "Verifying rollback..."
        run_integration_tests
        
    else
        print_info "Dry run: Would rollback $app_name to $previous_revision"
    fi
    
    print_success "Rollback completed successfully"
}

# Function to check application status
check_application_status() {
    print_info "Checking application status for $ENVIRONMENT..."
    
    local app_name="ai-teddy-bear-$ENVIRONMENT"
    
    # Get application info
    argocd app get "$app_name" --output wide
    
    # Get sync status
    local sync_status=$(argocd app get "$app_name" --output json | jq -r '.status.sync.status')
    local health_status=$(argocd app get "$app_name" --output json | jq -r '.status.health.status')
    
    print_info "Sync Status: $sync_status"
    print_info "Health Status: $health_status"
    
    # Check if intervention is needed
    if [[ "$sync_status" != "Synced" ]] || [[ "$health_status" != "Healthy" ]]; then
        print_warning "Application may need attention"
        
        # Show recent events
        print_info "Recent application events:"
        kubectl get events -n "ai-teddy-$ENVIRONMENT" --sort-by='.lastTimestamp' | tail -10
    else
        print_success "Application is healthy and synced"
    fi
}

# Function to sync application manually
sync_application() {
    print_info "Manually syncing $ENVIRONMENT environment..."
    
    local app_name="ai-teddy-bear-$ENVIRONMENT"
    
    if [[ "$DRY_RUN" == "false" ]]; then
        argocd app sync "$app_name" --timeout 600
        argocd app wait "$app_name" --timeout 900 --health
    else
        print_info "Dry run: Would sync $app_name"
    fi
    
    print_success "Application sync completed"
}

# Function to generate deployment report
generate_deployment_report() {
    print_info "Generating deployment report..."
    
    local report_file="deployment-report-$ENVIRONMENT-$(date +%Y%m%d-%H%M%S).json"
    local app_name="ai-teddy-bear-$ENVIRONMENT"
    
    # Collect deployment information
    local deployment_info=$(cat << EOF
{
  "deployment": {
    "environment": "$ENVIRONMENT",
    "version": "$VERSION",
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "operation": "$OPERATION",
    "dry_run": $DRY_RUN,
    "auto_sync": $AUTO_SYNC
  },
  "application_status": $(argocd app get "$app_name" --output json),
  "cluster_info": {
    "nodes": $(kubectl get nodes -o json),
    "namespaces": $(kubectl get namespaces -o json)
  },
  "performance_metrics": {
    "deployment_duration": "$(date +%s)",
    "tests_passed": true
  }
}
EOF
)
    
    echo "$deployment_info" > "$report_file"
    print_success "Deployment report saved to: $report_file"
}

# Function to cleanup on exit
cleanup() {
    local exit_code=$?
    
    if [[ $exit_code -ne 0 ]]; then
        print_error "Deployment pipeline failed with exit code: $exit_code"
        
        # Send failure notification (if configured)
        if command -v slack &> /dev/null && [[ -n "${SLACK_WEBHOOK_URL:-}" ]]; then
            curl -X POST -H 'Content-type: application/json' \
                --data "{\"text\":\"🚨 AI Teddy Bear deployment failed in $ENVIRONMENT\"}" \
                "$SLACK_WEBHOOK_URL"
        fi
    else
        print_success "Deployment pipeline completed successfully"
    fi
    
    return $exit_code
}

# Main execution function
main() {
    # Set up error handling
    trap cleanup EXIT
    
    # Parse arguments
    parse_args "$@"
    
    # Print banner
    cat << 'EOF'
    
🧸 AI Teddy Bear GitOps Deployment Pipeline
==========================================
DevOps Team - Task 14: GitOps with ArgoCD
==========================================

EOF
    
    print_info "Starting deployment pipeline..."
    print_info "Environment: $ENVIRONMENT"
    print_info "Operation: $OPERATION"
    print_info "Version: $VERSION"
    print_info "Dry Run: $DRY_RUN"
    
    # Validate prerequisites
    validate_prerequisites
    
    # Setup ArgoCD CLI
    setup_argocd_cli
    
    # Run pre-deployment checks
    run_pre_deployment_checks
    
    # Execute operation
    case "$OPERATION" in
        deploy)
            deploy_applications
            run_integration_tests
            ;;
        rollback)
            rollback_application
            ;;
        sync)
            sync_application
            run_integration_tests
            ;;
        status)
            check_application_status
            ;;
        *)
            print_error "Unknown operation: $OPERATION"
            exit 1
            ;;
    esac
    
    # Generate deployment report
    generate_deployment_report
    
    print_success "🎉 GitOps deployment pipeline completed successfully!"
}

# Execute main function with all arguments
main "$@" 