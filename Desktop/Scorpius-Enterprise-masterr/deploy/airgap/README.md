# Scorpius Enterprise Platform - Air-Gapped Deployment

This guide covers deploying Scorpius Enterprise Platform in air-gapped (disconnected) environments where internet access is restricted or unavailable.

## Overview

Air-gapped deployments require:
1. Pre-downloading all container images
2. Setting up private container registry
3. Configuring offline package repositories
4. Using local certificates and secrets
5. Modified Helm charts for offline operation

## Prerequisites

### Infrastructure Requirements
- Private Kubernetes cluster (EKS, OpenShift, or on-premises)
- Private container registry (Harbor, ECR, or similar)
- Internal DNS resolution
- Certificate Authority for TLS certificates
- Network Time Protocol (NTP) server
- LDAP/Active Directory for authentication

### Tools Required
- kubectl configured for your cluster
- Helm 3.8+
- Docker or Podman
- skopeo (for image synchronization)
- Local package mirrors (for Linux distributions)

## Pre-deployment Steps

### 1. Download Container Images

Create an image list and download all required images:

```bash
# Run this on a machine with internet access
./scripts/download-images.sh
```

Images include:
- Application services (wallet-guard, usage-metering, etc.)
- Infrastructure components (Redis, PostgreSQL, Prometheus)
- Kubernetes system images
- Base images (Alpine, Ubuntu)

### 2. Set Up Private Registry

```bash
# Push images to your private registry
./scripts/push-to-registry.sh <your-registry-url>
```

### 3. Configure DNS and Certificates

Set up internal DNS entries and generate TLS certificates for:
- `scorpius.internal.company.com`
- `api.scorpius.internal.company.com`
- `monitoring.scorpius.internal.company.com`

## Deployment Process

### 1. Configure Environment

```bash
export REGISTRY_URL="registry.internal.company.com"
export DOMAIN_NAME="scorpius.internal.company.com"
export ENVIRONMENT="airgap"
export NAMESPACE="scorpius-enterprise"
```

### 2. Create Namespace and Secrets

```bash
kubectl create namespace ${NAMESPACE}

# Container registry credentials
kubectl create secret docker-registry registry-secret \
  --docker-server=${REGISTRY_URL} \
  --docker-username=<username> \
  --docker-password=<password> \
  --namespace=${NAMESPACE}

# TLS certificates
kubectl create secret tls scorpius-tls \
  --cert=certs/scorpius.crt \
  --key=certs/scorpius.key \
  --namespace=${NAMESPACE}
```

### 3. Deploy Core Infrastructure

```bash
# Deploy PostgreSQL
helm install postgresql ./charts/postgresql \
  --namespace ${NAMESPACE} \
  --values values/airgap/postgresql-values.yaml

# Deploy Redis
helm install redis ./charts/redis \
  --namespace ${NAMESPACE} \
  --values values/airgap/redis-values.yaml

# Deploy monitoring stack
helm install monitoring ./charts/monitoring \
  --namespace ${NAMESPACE} \
  --values values/airgap/monitoring-values.yaml
```

### 4. Deploy Scorpius Applications

```bash
# Deploy all Scorpius services
helm install scorpius ./charts/scorpius \
  --namespace ${NAMESPACE} \
  --values values/airgap/scorpius-values.yaml
```

## Configuration Files

### Registry Configuration
All Helm values files are modified to use the private registry:

```yaml
image:
  registry: registry.internal.company.com
  repository: scorpius/wallet-guard
  tag: "1.0.0"
  pullPolicy: IfNotPresent
  pullSecrets:
    - name: registry-secret
```

### Network Policies
Strict network policies are enforced:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: scorpius-network-policy
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/part-of: scorpius
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: scorpius-enterprise
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: scorpius-enterprise
```

### Security Policies
Pod Security Standards are enforced:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: scorpius-enterprise
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

## Validation and Testing

### 1. Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n ${NAMESPACE}

# Check services are accessible
kubectl get svc -n ${NAMESPACE}

# Run health checks
./scripts/health-check.sh
```

### 2. Test Application Functionality

```bash
# Run integration tests
./scripts/test-airgap.sh

# Verify blockchain connectivity
./scripts/test-chains.sh
```

## Troubleshooting

### Common Issues

1. **Image pull failures**
   - Verify registry credentials
   - Check network connectivity to registry
   - Ensure images are properly tagged

2. **DNS resolution issues**
   - Configure CoreDNS with internal domains
   - Verify nameserver configuration

3. **Certificate validation errors**
   - Install internal CA certificates
   - Configure trust stores

4. **Time synchronization**
   - Ensure NTP is configured
   - Check cluster time drift

### Debug Commands

```bash
# Check image pull status
kubectl describe pod <pod-name> -n ${NAMESPACE}

# View application logs
kubectl logs -f deployment/<deployment-name> -n ${NAMESPACE}

# Test network connectivity
kubectl exec -it <pod-name> -n ${NAMESPACE} -- nslookup <service-name>
```

## Security Considerations

### Network Isolation
- All external network access is blocked
- Internal communication uses mTLS
- Network policies enforce zero-trust

### Image Security
- All images are scanned for vulnerabilities
- Images are signed and signatures verified
- Base images are hardened and minimal

### Secret Management
- External secret operator integration
- Secrets encrypted at rest
- Regular secret rotation

### Compliance
- All configurations meet enterprise security standards
- Audit logging is enabled and centralized
- Regulatory compliance (SOC2, ISO27001) maintained

## Maintenance

### Updates and Patches
- New versions require complete image refresh
- Rolling updates with blue-green deployment
- Rollback procedures documented

### Backup and Recovery
- Regular database backups to secure storage
- Configuration backups
- Disaster recovery procedures

### Monitoring
- Internal monitoring stack (Prometheus, Grafana)
- Alert routing to internal systems
- Log aggregation and analysis
