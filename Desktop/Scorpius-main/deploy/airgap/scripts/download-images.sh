#!/bin/bash
# Scorpius Enterprise Platform - Image Download Script
# Downloads all required container images for airgap deployment

set -euo pipefail

# Configuration
IMAGES_LIST="images.txt"
DOWNLOAD_DIR="./images"
LOG_FILE="download.log"

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

# Create images list if it doesn't exist
create_images_list() {
    if [[ ! -f "$IMAGES_LIST" ]]; then
        log "Creating images list..."
        cat > "$IMAGES_LIST" << 'EOF'
# Scorpius Application Images
scorpius/wallet-guard:1.0.0
scorpius/usage-metering:1.0.0
scorpius/auth-proxy:1.0.0
scorpius/audit-trail:1.0.0
scorpius/reporting:1.0.0

# Base Images
python:3.11-slim
node:18-alpine
nginx:1.25-alpine
redis:7.2-alpine
postgres:15-alpine

# Monitoring Stack
prom/prometheus:v2.45.0
grafana/grafana:10.0.0
prom/alertmanager:v0.25.0
prom/node-exporter:v1.6.0
prom/blackbox-exporter:v0.24.0

# Kubernetes Infrastructure
registry.k8s.io/kube-proxy:v1.28.0
registry.k8s.io/kube-apiserver:v1.28.0
registry.k8s.io/kube-controller-manager:v1.28.0
registry.k8s.io/kube-scheduler:v1.28.0
registry.k8s.io/etcd:3.5.9-0
registry.k8s.io/coredns/coredns:v1.10.1
registry.k8s.io/pause:3.9

# AWS Load Balancer Controller
public.ecr.aws/eks/aws-load-balancer-controller:v2.5.4

# Ingress Controllers
registry.k8s.io/ingress-nginx/controller:v1.8.1
registry.k8s.io/ingress-nginx/kube-webhook-certgen:v20230407

# Certificate Management
quay.io/jetstack/cert-manager-controller:v1.13.0
quay.io/jetstack/cert-manager-webhook:v1.13.0
quay.io/jetstack/cert-manager-cainjector:v1.13.0

# Security
falcosecurity/falco:0.35.1
falcosecurity/falco-driver-loader:0.35.1

# Backup and Storage
velero/velero:v1.11.1
velero/velero-plugin-for-aws:v1.7.1

# Service Mesh (optional)
istio/pilot:1.18.2
istio/proxyv2:1.18.2
istio/operator:1.18.2
EOF
        log "Images list created at $IMAGES_LIST"
    fi
}

# Download single image
download_image() {
    local image="$1"
    local filename
    filename=$(echo "$image" | tr '/' '_' | tr ':' '_')
    
    log "Downloading $image..."
    
    if docker pull "$image"; then
        docker save "$image" -o "$DOWNLOAD_DIR/${filename}.tar"
        log "✓ Downloaded and saved: $image"
        return 0
    else
        error "✗ Failed to download: $image"
        return 1
    fi
}

# Main download function
download_all_images() {
    local failed_images=()
    local total_images=0
    local successful_downloads=0
    
    log "Starting image download process..."
    
    # Create download directory
    mkdir -p "$DOWNLOAD_DIR"
    
    # Count total images
    total_images=$(grep -v '^#' "$IMAGES_LIST" | grep -v '^$' | wc -l)
    log "Total images to download: $total_images"
    
    # Download each image
    while IFS= read -r image; do
        # Skip comments and empty lines
        [[ "$image" =~ ^#.*$ ]] && continue
        [[ -z "$image" ]] && continue
        
        if download_image "$image"; then
            ((successful_downloads++))
        else
            failed_images+=("$image")
        fi
    done < "$IMAGES_LIST"
    
    # Summary
    log "Download complete!"
    log "Successfully downloaded: $successful_downloads/$total_images images"
    
    if [[ ${#failed_images[@]} -gt 0 ]]; then
        warn "Failed to download the following images:"
        for img in "${failed_images[@]}"; do
            warn "  - $img"
        done
        return 1
    fi
    
    return 0
}

# Generate manifest file
generate_manifest() {
    log "Generating image manifest..."
    
    cat > "$DOWNLOAD_DIR/manifest.json" << EOF
{
  "generated": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "version": "1.0",
  "images": [
EOF
    
    local first=true
    while IFS= read -r image; do
        [[ "$image" =~ ^#.*$ ]] && continue
        [[ -z "$image" ]] && continue
        
        if [[ "$first" == true ]]; then
            first=false
        else
            echo "," >> "$DOWNLOAD_DIR/manifest.json"
        fi
        
        echo -n "    \"$image\"" >> "$DOWNLOAD_DIR/manifest.json"
    done < "$IMAGES_LIST"
    
    cat >> "$DOWNLOAD_DIR/manifest.json" << EOF

  ]
}
EOF
    
    log "Manifest generated at $DOWNLOAD_DIR/manifest.json"
}

# Calculate total size
calculate_size() {
    if [[ -d "$DOWNLOAD_DIR" ]]; then
        local size
        size=$(du -sh "$DOWNLOAD_DIR" | cut -f1)
        log "Total download size: $size"
    fi
}

# Verify downloads
verify_downloads() {
    log "Verifying downloaded images..."
    
    local verification_failed=false
    
    while IFS= read -r image; do
        [[ "$image" =~ ^#.*$ ]] && continue
        [[ -z "$image" ]] && continue
        
        local filename
        filename=$(echo "$image" | tr '/' '_' | tr ':' '_')
        local filepath="$DOWNLOAD_DIR/${filename}.tar"
        
        if [[ -f "$filepath" ]]; then
            if docker load -i "$filepath" > /dev/null 2>&1; then
                log "✓ Verified: $image"
            else
                error "✗ Corrupted archive: $filepath"
                verification_failed=true
            fi
        else
            error "✗ Missing file: $filepath"
            verification_failed=true
        fi
    done < "$IMAGES_LIST"
    
    if [[ "$verification_failed" == true ]]; then
        error "Image verification failed!"
        return 1
    else
        log "All images verified successfully!"
        return 0
    fi
}

# Cleanup function
cleanup() {
    log "Cleaning up Docker images from local registry..."
    
    while IFS= read -r image; do
        [[ "$image" =~ ^#.*$ ]] && continue
        [[ -z "$image" ]] && continue
        
        docker rmi "$image" > /dev/null 2>&1 || true
    done < "$IMAGES_LIST"
    
    log "Cleanup complete"
}

# Main execution
main() {
    log "Scorpius Enterprise Platform - Image Download Script"
    log "=================================================="
    
    # Check prerequisites
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! docker info > /dev/null 2>&1; then
        error "Docker daemon is not running"
        exit 1
    fi
    
    # Create images list
    create_images_list
    
    # Download images
    if download_all_images; then
        generate_manifest
        calculate_size
        
        # Verify downloads
        if verify_downloads; then
            log "All operations completed successfully!"
            
            # Optional cleanup
            read -p "Do you want to remove images from local Docker registry to save space? (y/n): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                cleanup
            fi
        else
            error "Verification failed. Please check the logs and retry."
            exit 1
        fi
    else
        error "Download process failed. Please check the logs and retry."
        exit 1
    fi
}

# Handle script interruption
trap 'error "Script interrupted"; exit 1' INT TERM

# Execute main function
main "$@"
