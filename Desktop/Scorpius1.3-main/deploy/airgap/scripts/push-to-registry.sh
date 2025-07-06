#!/bin/bash
# Scorpius Enterprise Platform - Registry Push Script
# Pushes all downloaded images to private registry

set -euo pipefail

# Configuration
DOWNLOAD_DIR="./images"
MANIFEST_FILE="$DOWNLOAD_DIR/manifest.json"
LOG_FILE="push.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" | tee -a "$LOG_FILE"
}

# Usage function
usage() {
    cat << EOF
Usage: $0 <registry-url> [options]

Arguments:
  registry-url    Target private registry URL (e.g., registry.company.com)

Options:
  -u, --username  Registry username
  -p, --password  Registry password
  -n, --namespace Registry namespace (default: scorpius)
  -f, --force     Force push even if image exists
  -t, --tag       Additional tag to apply (default: latest)
  -h, --help      Show this help message

Examples:
  $0 registry.company.com
  $0 registry.company.com -u admin -p password
  $0 harbor.internal.com -n enterprise -t v1.0.0
EOF
    exit 1
}

# Parse command line arguments
parse_args() {
    if [[ $# -eq 0 ]]; then
        error "Registry URL is required"
        usage
    fi
    
    REGISTRY_URL="$1"
    shift
    
    # Default values
    USERNAME=""
    PASSWORD=""
    NAMESPACE="scorpius"
    FORCE_PUSH=false
    ADDITIONAL_TAG="latest"
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -u|--username)
                USERNAME="$2"
                shift 2
                ;;
            -p|--password)
                PASSWORD="$2"
                shift 2
                ;;
            -n|--namespace)
                NAMESPACE="$2"
                shift 2
                ;;
            -f|--force)
                FORCE_PUSH=true
                shift
                ;;
            -t|--tag)
                ADDITIONAL_TAG="$2"
                shift 2
                ;;
            -h|--help)
                usage
                ;;
            *)
                error "Unknown option: $1"
                usage
                ;;
        esac
    done
}

# Registry login
registry_login() {
    if [[ -n "$USERNAME" && -n "$PASSWORD" ]]; then
        log "Logging into registry $REGISTRY_URL..."
        if echo "$PASSWORD" | docker login "$REGISTRY_URL" -u "$USERNAME" --password-stdin; then
            log "✓ Registry login successful"
            return 0
        else
            error "✗ Registry login failed"
            return 1
        fi
    else
        log "No credentials provided, assuming already logged in or using existing credentials"
        return 0
    fi
}

# Load image from tar file
load_image() {
    local image="$1"
    local filename
    filename=$(echo "$image" | tr '/' '_' | tr ':' '_')
    local filepath="$DOWNLOAD_DIR/${filename}.tar"
    
    if [[ ! -f "$filepath" ]]; then
        error "Image file not found: $filepath"
        return 1
    fi
    
    log "Loading image from $filepath..."
    if docker load -i "$filepath"; then
        log "✓ Loaded: $image"
        return 0
    else
        error "✗ Failed to load: $filepath"
        return 1
    fi
}

# Tag image for private registry
tag_image() {
    local original_image="$1"
    local target_image="$2"
    
    log "Tagging $original_image as $target_image..."
    if docker tag "$original_image" "$target_image"; then
        log "✓ Tagged: $target_image"
        return 0
    else
        error "✗ Failed to tag: $original_image"
        return 1
    fi
}

# Push image to registry
push_image() {
    local image="$1"
    
    log "Pushing $image..."
    if docker push "$image"; then
        log "✓ Pushed: $image"
        return 0
    else
        error "✗ Failed to push: $image"
        return 1
    fi
}

# Check if image exists in registry
image_exists() {
    local image="$1"
    
    # Try to pull the manifest without downloading the image
    if docker manifest inspect "$image" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Convert image name to private registry format
convert_image_name() {
    local original_image="$1"
    local image_name
    local image_tag
    
    # Extract image name and tag
    if [[ "$original_image" == *":"* ]]; then
        image_name="${original_image%:*}"
        image_tag="${original_image#*:}"
    else
        image_name="$original_image"
        image_tag="latest"
    fi
    
    # Remove registry prefix if present
    if [[ "$image_name" == *"/"* ]]; then
        # For multi-part names like "prom/prometheus", keep the last two parts
        if [[ $(echo "$image_name" | tr -cd '/' | wc -c) -gt 1 ]]; then
            image_name=$(echo "$image_name" | rev | cut -d'/' -f1-2 | rev)
        else
            # For single part names like "nginx", keep as is but remove registry
            image_name=$(echo "$image_name" | rev | cut -d'/' -f1 | rev)
        fi
    fi
    
    # Construct new image name
    echo "$REGISTRY_URL/$NAMESPACE/$image_name:$image_tag"
}

# Process single image
process_image() {
    local original_image="$1"
    local target_image
    target_image=$(convert_image_name "$original_image")
    
    log "Processing $original_image -> $target_image"
    
    # Check if image already exists (unless force push)
    if [[ "$FORCE_PUSH" == false ]] && image_exists "$target_image"; then
        warn "Image already exists: $target_image (use -f to force push)"
        return 0
    fi
    
    # Load image
    if ! load_image "$original_image"; then
        return 1
    fi
    
    # Tag image
    if ! tag_image "$original_image" "$target_image"; then
        return 1
    fi
    
    # Tag with additional tag if specified
    if [[ "$ADDITIONAL_TAG" != "latest" ]]; then
        local additional_target_image
        additional_target_image=$(echo "$target_image" | sed "s/:.*/:$ADDITIONAL_TAG/")
        if ! tag_image "$original_image" "$additional_target_image"; then
            warn "Failed to apply additional tag: $additional_target_image"
        else
            if ! push_image "$additional_target_image"; then
                warn "Failed to push additional tagged image: $additional_target_image"
            fi
        fi
    fi
    
    # Push image
    if ! push_image "$target_image"; then
        return 1
    fi
    
    # Clean up local tagged image
    docker rmi "$target_image" > /dev/null 2>&1 || true
    
    return 0
}

# Generate values file for private registry
generate_values_file() {
    log "Generating Helm values file for private registry..."
    
    cat > "values/airgap/registry-values.yaml" << EOF
# Scorpius Enterprise Platform - Private Registry Configuration
# Generated on $(date)

global:
  registry:
    url: "$REGISTRY_URL"
    namespace: "$NAMESPACE"
    pullPolicy: IfNotPresent
    pullSecrets:
      - name: registry-secret

images:
  walletGuard:
    repository: $REGISTRY_URL/$NAMESPACE/wallet-guard
    tag: "1.0.0"
  
  usageMetering:
    repository: $REGISTRY_URL/$NAMESPACE/usage-metering
    tag: "1.0.0"
  
  authProxy:
    repository: $REGISTRY_URL/$NAMESPACE/auth-proxy
    tag: "1.0.0"
  
  auditTrail:
    repository: $REGISTRY_URL/$NAMESPACE/audit-trail
    tag: "1.0.0"
    
  reporting:
    repository: $REGISTRY_URL/$NAMESPACE/reporting
    tag: "1.0.0"

infrastructure:
  redis:
    image:
      registry: $REGISTRY_URL
      repository: $NAMESPACE/redis
      tag: "7.2-alpine"
  
  postgresql:
    image:
      registry: $REGISTRY_URL
      repository: $NAMESPACE/postgres
      tag: "15-alpine"
  
  nginx:
    image:
      registry: $REGISTRY_URL
      repository: $NAMESPACE/nginx
      tag: "1.25-alpine"

monitoring:
  prometheus:
    image:
      registry: $REGISTRY_URL
      repository: $NAMESPACE/prometheus
      tag: "v2.45.0"
  
  grafana:
    image:
      registry: $REGISTRY_URL
      repository: $NAMESPACE/grafana
      tag: "10.0.0"
  
  alertmanager:
    image:
      registry: $REGISTRY_URL
      repository: $NAMESPACE/alertmanager
      tag: "v0.25.0"

# Network configuration for airgap environment
networking:
  ingress:
    enabled: true
    className: "nginx"
    annotations:
      cert-manager.io/cluster-issuer: "internal-ca-issuer"
    hosts:
      - host: scorpius.internal.company.com
        paths:
          - path: /
            pathType: Prefix
    tls:
      - secretName: scorpius-tls
        hosts:
          - scorpius.internal.company.com

# Security configuration
security:
  networkPolicies:
    enabled: true
  podSecurityStandards:
    enforced: true
  serviceAccount:
    create: true
    annotations: {}

# Resource limits for enterprise deployment
resources:
  walletGuard:
    limits:
      cpu: 1000m
      memory: 1Gi
    requests:
      cpu: 500m
      memory: 512Mi
  
  usageMetering:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 250m
      memory: 256Mi
EOF
    
    mkdir -p "values/airgap"
    log "✓ Values file generated at values/airgap/registry-values.yaml"
}

# Main processing function
process_all_images() {
    if [[ ! -f "$MANIFEST_FILE" ]]; then
        error "Manifest file not found: $MANIFEST_FILE"
        error "Please run download-images.sh first"
        return 1
    fi
    
    local failed_images=()
    local total_images
    local successful_pushes=0
    
    # Extract images from manifest
    local images
    images=$(jq -r '.images[]' "$MANIFEST_FILE")
    total_images=$(echo "$images" | wc -l)
    
    log "Starting image push process..."
    log "Target registry: $REGISTRY_URL"
    log "Namespace: $NAMESPACE"
    log "Total images to push: $total_images"
    
    # Process each image
    while IFS= read -r image; do
        if process_image "$image"; then
            ((successful_pushes++))
        else
            failed_images+=("$image")
        fi
    done <<< "$images"
    
    # Summary
    log "Push process complete!"
    log "Successfully pushed: $successful_pushes/$total_images images"
    
    if [[ ${#failed_images[@]} -gt 0 ]]; then
        warn "Failed to push the following images:"
        for img in "${failed_images[@]}"; do
            warn "  - $img"
        done
        return 1
    fi
    
    return 0
}

# Main execution
main() {
    log "Scorpius Enterprise Platform - Registry Push Script"
    log "================================================="
    
    # Parse arguments
    parse_args "$@"
    
    # Check prerequisites
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! command -v jq &> /dev/null; then
        error "jq is not installed or not in PATH"
        exit 1
    fi
    
    if ! docker info > /dev/null 2>&1; then
        error "Docker daemon is not running"
        exit 1
    fi
    
    # Check if download directory exists
    if [[ ! -d "$DOWNLOAD_DIR" ]]; then
        error "Download directory not found: $DOWNLOAD_DIR"
        error "Please run download-images.sh first"
        exit 1
    fi
    
    # Login to registry
    if ! registry_login; then
        error "Registry login failed"
        exit 1
    fi
    
    # Process all images
    if process_all_images; then
        log "All images pushed successfully!"
        generate_values_file
        log "Setup complete! You can now deploy using the generated values file."
    else
        error "Push process failed. Please check the logs and retry."
        exit 1
    fi
}

# Handle script interruption
trap 'error "Script interrupted"; exit 1' INT TERM

# Execute main function
main "$@"
