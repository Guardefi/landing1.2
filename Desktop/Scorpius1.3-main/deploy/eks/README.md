# Scorpius Enterprise Platform - EKS Deployment Guide

This comprehensive guide covers deploying Scorpius Enterprise Platform to AWS EKS in multiple configurations including production, airgap, and development environments.

## 🏗️ Architecture Overview

Scorpius Enterprise Platform on EKS includes:

- **Application Services**: Wallet Guard, Usage Metering, Auth Proxy, Audit Trail, Reporting
- **Infrastructure**: PostgreSQL, Redis, NGINX Ingress, Load Balancer
- **Monitoring**: Prometheus, Grafana, Alertmanager, Custom Dashboards
- **Security**: Network Policies, RBAC, Pod Security Standards, TLS Encryption
- **Compliance**: Audit Logging, Backup/Recovery, SOC2/ISO27001 Controls

## 📋 Prerequisites

### Required Tools
- AWS CLI v2.x configured with appropriate credentials
- Terraform >= 1.0
- kubectl >= 1.28
- Helm >= 3.8
- Docker (for building custom images)
- jq (for JSON processing)

### AWS Permissions
Your AWS credentials must have permissions for:
- EKS cluster management
- VPC and networking resources
- RDS and ElastiCache
- IAM roles and policies
- CloudWatch and logging
- ACM certificate management
- Route53 DNS management
- AWS Backup services
- QLDB ledger management
- S3 buckets for Terraform state
- DynamoDB for Terraform locking

### Infrastructure Prerequisites
- S3 bucket for Terraform state storage
- DynamoDB table for Terraform state locking  
- Route53 hosted zone for your domain
- ACM certificate (optional - can be created during deployment)

## 🚀 Quick Start (Standard Deployment)

### 1. Configure Environment Variables

```bash
export AWS_REGION="us-west-2"
export ENVIRONMENT="prod"
export DOMAIN_NAME="scorpius.your-company.com"
export TERRAFORM_STATE_BUCKET="your-terraform-state-bucket"
export TERRAFORM_LOCK_TABLE="your-terraform-lock-table"
export CLUSTER_NAME="scorpius-enterprise"
```

### 2. Initialize Terraform

```bash
cd deploy/eks
terraform init
```

### 3. Create terraform.tfvars

```hcl
# Basic Configuration
aws_region    = "us-west-2"
environment   = "prod"
owner         = "platform-team@your-company.com"
cost_center   = "engineering"

# State Configuration
terraform_state_bucket = "your-terraform-state-bucket"
terraform_lock_table   = "your-terraform-lock-table"

# Domain Configuration  
domain_name     = "scorpius.your-company.com"
hosted_zone_id  = "Z1234567890ABC"

# Network Configuration
vpc_cidr        = "10.0.0.0/16"
private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

# EKS Configuration
cluster_version = "1.28"

# Database Configuration
rds_instance_class       = "db.r6g.large"
rds_allocated_storage    = 100
rds_backup_retention_period = 30

# Redis Configuration
redis_node_type         = "cache.r6g.large"
redis_num_cache_nodes   = 2

# Application Configuration
replicas = 3
resources = {
  requests = {
    cpu    = "500m"
    memory = "1Gi"
  }
  limits = {
    cpu    = "2000m"
    memory = "4Gi"
  }
}
```

### 4. Plan and Apply

```bash
# Review the deployment plan
terraform plan

# Apply the configuration
terraform apply
```

### 5. Configure kubectl

```bash
aws eks update-kubeconfig --region $AWS_REGION --name scorpius-enterprise-prod
```

### 6. Deploy Application

```bash
# Install Helm charts
helm repo add scorpius ./helm
helm install scorpius-enterprise scorpius/scorpius \
  --namespace scorpius \
  --create-namespace \
  --values deploy/helm/values/production.yaml
```

## Architecture Overview

The deployment creates:

### Network Infrastructure
- VPC with public/private subnets across 3 AZs
- NAT gateways for outbound internet access
- Security groups with least-privilege access

### EKS Cluster
- Managed Kubernetes cluster (v1.28)
- Multiple node groups:
  - System nodes (t3.medium) for platform services
  - Application nodes (t3.large/xlarge) for workloads
  - Scanner nodes (r5.2xlarge) for heavy analysis

### Data Layer
- RDS PostgreSQL cluster with read replicas
- ElastiCache Redis cluster for caching
- QLDB ledger for immutable audit trails

### Security & Monitoring
- IAM roles with OIDC integration
- CloudWatch logging and monitoring
- Application Load Balancer with TLS termination
- AWS Backup for automated backups

## Post-Deployment Configuration

### 1. SSL Certificate Validation
Verify your SSL certificate in ACM console and update DNS records if needed.

### 2. Configure Monitoring
Access Grafana dashboard:
```bash
kubectl port-forward -n monitoring svc/grafana 3000:80
```

### 3. Set Up Alerting
Configure Slack/email notifications in AlertManager:
```bash
kubectl edit configmap -n monitoring alertmanager-config
```

### 4. Initialize Database
Run database migrations:
```bash
kubectl exec -n scorpius deployment/api-gateway -- python manage.py migrate
```

### 5. Create Admin User
```bash
kubectl exec -n scorpius deployment/api-gateway -- python manage.py createsuperuser
```

## Scaling Configuration

### Auto-scaling
The deployment includes:
- Cluster Autoscaler for node scaling
- Horizontal Pod Autoscaler for application scaling
- Vertical Pod Autoscaler recommendations

### Manual Scaling
Scale node groups:
```bash
aws eks update-nodegroup-config \
  --cluster-name scorpius-enterprise-prod \
  --nodegroup-name application \
  --scaling-config minSize=5,maxSize=20,desiredSize=10
```

## Backup and Disaster Recovery

### Automated Backups
- RDS automated backups (30-day retention)
- QLDB automatic backups
- EBS volume snapshots
- Application data backups via AWS Backup

### Manual Backup
```bash
# Create manual RDS snapshot
aws rds create-db-cluster-snapshot \
  --db-cluster-snapshot-identifier scorpius-manual-$(date +%Y%m%d) \
  --db-cluster-identifier scorpius-enterprise-prod-postgres
```

### Restore Procedure
1. Restore RDS from snapshot
2. Restore Redis from backup
3. Redeploy application with new endpoints
4. Verify data integrity

## Monitoring and Alerting

### Key Metrics
- API latency (p95 < 2.5s SLA)
- Error rate (< 2% SLA)
- System resource utilization
- Database performance
- Security scan completion rates

### Alert Channels
- Slack: #scorpius-alerts
- Email: oncall@your-company.com
- PagerDuty: Critical incidents

### Dashboards
- Platform Overview: Service health and performance
- Business Metrics: Usage, scans, revenue
- Security Dashboard: Threat detection and response

## Security Hardening

### Network Security
- Private subnets for all workloads
- Security groups with minimal required access
- WAF protection on ALB
- VPC Flow Logs enabled

### Application Security
- RBAC with least privilege
- Service mesh with mTLS
- Secrets stored in AWS Secrets Manager
- Image scanning enabled

### Compliance
- Audit logs in QLDB
- Resource tagging for governance
- Backup encryption at rest
- Network traffic encryption

## Troubleshooting

### Common Issues

#### 1. EKS Cluster Access Denied
```bash
# Update IAM mapping
kubectl edit configmap -n kube-system aws-auth
```

#### 2. Database Connection Issues
```bash
# Check security groups
aws ec2 describe-security-groups --group-ids sg-xxx
```

#### 3. Certificate Issues
```bash
# Check certificate status
aws acm describe-certificate --certificate-arn arn:aws:acm:xxx
```

### Logs Access
```bash
# View application logs
kubectl logs -n scorpius deployment/api-gateway

# View cluster logs
aws logs describe-log-groups --log-group-name-prefix "/aws/eks"
```

## Maintenance

### Updates
- Kubernetes cluster updates (quarterly)
- Node group AMI updates (monthly)  
- Application deployments (continuous)

### Cost Optimization
- Reserved instances for predictable workloads
- Spot instances for batch processing
- Automated resource right-sizing
- Unused resource cleanup

## Support

### Documentation
- [Architecture Guide](..\..\docs\architecture)
- [Security Policy](..\..\docs\security)
- [API Documentation](..\..\docs\api)

### Contact
- Platform Team: platform@your-company.com
- On-call: +1-555-ONCALL
- Slack: #scorpius-support

---

**Estimated Deployment Time**: 45-60 minutes
**Monthly Cost (Production)**: $2,000-4,000 USD
**SLA**: 99.9% uptime

# Test the deployment
./scripts/test-deployment.sh
````markdown
## 🔧 Advanced Deployment Options

### Multi-Environment Setup

For organizations managing multiple environments:

```bash
# Development
terraform workspace new dev
terraform apply -var-file="environments/dev.tfvars"

# Staging  
terraform workspace new staging
terraform apply -var-file="environments/staging.tfvars"

# Production
terraform workspace new prod
terraform apply -var-file="environments/prod.tfvars"
```

### High Availability Configuration

For mission-critical deployments:

```hcl
# terraform.tfvars
cluster_version = "1.28"

node_groups = {
  system = {
    instance_types = ["m5.large", "m5.xlarge"]
    capacity_type  = "ON_DEMAND"
    min_size       = 3
    max_size       = 10
    desired_size   = 3
    disk_size      = 100
    labels = {
      role = "system"
    }
    taints = [
      {
        key    = "system-workload"
        value  = "true"
        effect = "NO_SCHEDULE"
      }
    ]
  }
  application = {
    instance_types = ["m5.xlarge", "m5.2xlarge"]
    capacity_type  = "SPOT"
    min_size       = 5
    max_size       = 20
    desired_size   = 5
    disk_size      = 200
    labels = {
      role = "application"
    }
  }
}

# Enable high availability for data layer
rds_multi_az = true
rds_backup_retention_period = 7
elasticache_num_cache_nodes = 3
```

### Custom Networking

For specific networking requirements:

```hcl
# Custom VPC configuration
vpc_cidr = "172.16.0.0/16"
private_subnets = ["172.16.1.0/24", "172.16.2.0/24", "172.16.3.0/24"]
public_subnets = ["172.16.101.0/24", "172.16.102.0/24", "172.16.103.0/24"]

# Custom security groups
additional_security_groups = ["sg-12345678", "sg-87654321"]

# Private cluster endpoint
cluster_endpoint_private_access = true
cluster_endpoint_public_access = false
cluster_endpoint_public_access_cidrs = ["10.0.0.0/8"]
```

## 🛠️ Kustomize Deployment (Alternative)

For Kubernetes-native deployments using Kustomize:

### Base Deployment

```bash
# Deploy base configuration
kubectl apply -k deploy/kustomize/base
```

### Production Overlay

```bash
# Deploy production configuration
kubectl apply -k deploy/kustomize/overlays/production
```

### Airgap Deployment

```bash
# Deploy airgap configuration (for disconnected environments)
kubectl apply -k deploy/kustomize/overlays/airgap
```

## 🔒 Air-Gap Deployment

For environments without internet access, see the dedicated [Air-Gap Deployment Guide](..\airgap\README.md).

Quick setup:

```bash
# 1. Download images (on connected machine)
cd deploy/airgap
./scripts/download-images.sh

# 2. Push to private registry
./scripts/push-to-registry.sh registry.internal.company.com

# 3. Deploy using private registry
helm install scorpius ./charts/scorpius \
  --namespace scorpius-enterprise \
  --values values/airgap/scorpius-values.yaml
```

## 🧪 Testing & Validation

### Automated Testing

Run the comprehensive test suite:

```bash
# Full deployment test
./scripts/test-deployment.sh

# Specific test categories
./scripts/test-deployment.sh --tests=connectivity,security,performance

# Generate detailed report
./scripts/test-deployment.sh --report --output=deployment-report.html
```

### Manual Validation

```bash
# 1. Verify cluster status
kubectl cluster-info
kubectl get nodes -o wide

# 2. Check application pods
kubectl get pods -n scorpius-enterprise -o wide

# 3. Test service endpoints
kubectl port-forward svc/wallet-guard-service 8080:8000 -n scorpius-enterprise
curl http://localhost:8080/health

# 4. Verify monitoring stack
kubectl port-forward svc/grafana 3000:3000 -n monitoring
# Access Grafana at http://localhost:3000

# 5. Check ingress
kubectl get ingress -n scorpius-enterprise
```

### Load Testing

```bash
# Install load testing tools
helm install k6-operator grafana/k6-operator

# Run performance tests
kubectl apply -f tests/load-test-config.yaml

# Monitor results
kubectl logs -f jobs/scorpius-load-test
```

### Security Validation

```bash
# Scan for security issues
kubectl apply -f https://raw.githubusercontent.com/aquasecurity/kube-bench/main/job.yaml

# Check network policies
kubectl get networkpolicy -A

# Validate RBAC
kubectl auth can-i --list --as=system:serviceaccount:scorpius-enterprise:scorpius-service-account
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Pods in Pending State

```bash
# Check resource availability
kubectl describe node

# Check pod events
kubectl describe pod <pod-name> -n scorpius-enterprise

# Check resource quotas
kubectl get resourcequota -n scorpius-enterprise
```

#### 2. Service Connection Issues

```bash
# Check service endpoints
kubectl get endpoints -n scorpius-enterprise

# Test internal DNS
kubectl run debug --image=busybox --rm -it -- nslookup wallet-guard-service.scorpius-enterprise.svc.cluster.local

# Check network policies
kubectl get networkpolicy -n scorpius-enterprise -o yaml
```

#### 3. Database Connection Problems

```bash
# Check database status
kubectl logs -l app=postgresql -n scorpius-enterprise

# Test connectivity
kubectl run db-test --image=postgres:15 --rm -it --env="PGPASSWORD=<password>" -- psql -h postgresql-service -U scorpius -d scorpius

# Check secrets
kubectl get secret database-secrets -n scorpius-enterprise -o yaml
```

#### 4. TLS Certificate Issues

```bash
# Check certificate status
kubectl get certificate -n scorpius-enterprise

# Check cert-manager logs
kubectl logs -l app=cert-manager -n cert-manager

# Verify ingress TLS
kubectl describe ingress scorpius-ingress -n scorpius-enterprise
```

#### 5. Monitoring Stack Issues

```bash
# Check Prometheus targets
kubectl port-forward svc/prometheus 9090:9090 -n monitoring
# Visit http://localhost:9090/targets

# Check Grafana data sources
kubectl port-forward svc/grafana 3000:3000 -n monitoring
# Visit http://localhost:3000

# Verify metrics collection
kubectl exec -it deployment/prometheus -n monitoring -- promtool query instant 'up'
```

### Debug Commands

```bash
# Get cluster information
kubectl cluster-info dump > cluster-debug.txt

# Check resource usage
kubectl top nodes
kubectl top pods -n scorpius-enterprise

# Describe all resources in namespace
kubectl describe all -n scorpius-enterprise > namespace-debug.txt

# Check events
kubectl get events -n scorpius-enterprise --sort-by='.lastTimestamp'

# Export configurations
kubectl get all -n scorpius-enterprise -o yaml > deployment-config.yaml
```

## 📊 Monitoring & Observability

### Dashboards

Pre-configured Grafana dashboards:

- **SLA Dashboard**: Service uptime, response times, error rates
- **Usage Dashboard**: API calls, billing metrics, resource utilization  
- **Security Dashboard**: Authentication events, threat detection
- **Infrastructure Dashboard**: Cluster health, node metrics, storage

Access: `https://monitoring.${DOMAIN_NAME}/dashboards`

### Alerts

Key alerts configured:

- **High Error Rate**: >5% error rate for 5 minutes
- **Response Time**: >2s average response time
- **Pod Restart**: Pod restarts >3 times in 10 minutes
- **Resource Usage**: CPU/Memory >80% for 10 minutes
- **Certificate Expiry**: TLS certificates expiring in <30 days
- **Backup Failures**: Backup job failures

### Logs

Centralized logging with structured output:

```bash
# Application logs
kubectl logs -l app.kubernetes.io/part-of=scorpius-enterprise -n scorpius-enterprise

# Audit logs
kubectl logs -l app=audit-trail -n scorpius-enterprise

# System logs
kubectl logs -l component=kube-apiserver -n kube-system
```

## 💾 Backup & Recovery

### Automated Backups

```bash
# Database backups (daily)
kubectl get cronjob postgresql-backup -n scorpius-enterprise

# Application data backups (using Velero)
velero backup create scorpius-backup --include-namespaces scorpius-enterprise

# Configuration backups
kubectl get configmap,secret -n scorpius-enterprise -o yaml > backup/configs-$(date +%Y%m%d).yaml
```

### Disaster Recovery

```bash
# Restore from backup
velero restore create --from-backup scorpius-backup

# Restore database
kubectl exec -it postgresql-primary-0 -n scorpius-enterprise -- pg_restore -d scorpius /backups/latest.sql

# Verify restoration
./scripts/test-deployment.sh
```

## 🔄 Updates & Maintenance

### Application Updates

```bash
# Update application images
helm upgrade scorpius ./charts/scorpius \
  --namespace scorpius-enterprise \
  --set image.tag=1.1.0 \
  --values values/production.yaml

# Rolling restart
kubectl rollout restart deployment -n scorpius-enterprise

# Verify update
kubectl rollout status deployment/wallet-guard -n scorpius-enterprise
```

### Cluster Updates

```bash
# Update EKS cluster
terraform plan -var="cluster_version=1.29"
terraform apply

# Update node groups
terraform plan -var="node_group_version=1.29"
terraform apply

# Verify cluster health
kubectl get nodes
./scripts/test-deployment.sh
```

### Security Updates

```bash
# Update container images for security patches
./scripts/update-security-patches.sh

# Rotate secrets
kubectl create secret generic scorpius-secrets-new --from-env-file=.env.prod
kubectl patch deployment wallet-guard -p '{"spec":{"template":{"spec":{"volumes":[{"name":"secrets","secret":{"secretName":"scorpius-secrets-new"}}]}}}}'

# Update TLS certificates
cert-manager renew --all
```

## 📈 Scaling

### Horizontal Pod Autoscaling

```bash
# Enable HPA
kubectl apply -f manifests/hpa.yaml

# Check scaling status
kubectl get hpa -n scorpius-enterprise

# Manual scaling
kubectl scale deployment wallet-guard --replicas=5 -n scorpius-enterprise
```

### Cluster Autoscaling

```bash
# Configure cluster autoscaler
helm install cluster-autoscaler autoscaler/cluster-autoscaler \
  --set autoDiscovery.clusterName=$CLUSTER_NAME \
  --set awsRegion=$AWS_REGION

# Monitor scaling events
kubectl logs -l app=cluster-autoscaler -n kube-system
```

### Vertical Pod Autoscaling

```bash
# Install VPA
kubectl apply -f https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler/deploy

# Configure VPA
kubectl apply -f manifests/vpa.yaml

# Check recommendations
kubectl describe vpa -n scorpius-enterprise
```

## 🔐 Security Best Practices

### Network Security

- Network policies enforce zero-trust communication
- Private subnets for application workloads
- WAF protection for public endpoints
- VPC Flow Logs enabled

### Identity & Access Management

- OIDC integration with EKS
- Service accounts with minimal permissions
- Regular credential rotation
- Multi-factor authentication required

### Data Protection

- Encryption in transit (TLS 1.3)
- Encryption at rest (AWS KMS)
- Database backups encrypted
- Secrets management with external secrets operator

### Compliance

- SOC2 Type II controls implemented
- ISO27001 security framework
- Regular security scanning
- Audit trail for all operations

## 📞 Support & Contact

For deployment issues or questions:

- **Documentation**: [Enterprise Documentation](..\..\docs)
- **Issues**: [GitHub Issues](https://github.com/company/scorpius-enterprise/issues)
- **Support**: support@company.com
- **Emergency**: +1-800-SCORPIUS

---

## 📋 Deployment Checklist

- [ ] Prerequisites installed and configured
- [ ] AWS credentials configured with required permissions
- [ ] Terraform state backend configured
- [ ] Domain name and DNS configured
- [ ] SSL certificates available
- [ ] terraform.tfvars file created and validated
- [ ] Infrastructure deployed (`terraform apply`)
- [ ] Application deployed (`helm install`)
- [ ] Tests passed (`./scripts/test-deployment.sh`)
- [ ] Monitoring configured and accessible
- [ ] Backup schedules configured
- [ ] Security scan completed
- [ ] Documentation reviewed
- [ ] Team trained on operations

**Estimated deployment time**: 45-60 minutes for standard deployment, 2-3 hours for high-availability production setup.

---

*Last updated: June 26, 2025*
*Version: 1.0.0*
