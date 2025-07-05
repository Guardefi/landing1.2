# Scorpius Enterprise Platform - Private Cloud Deployment Guide

## 🚀 Executive Summary

This guide provides comprehensive instructions for deploying Scorpius Enterprise Platform in private cloud environments. The platform supports air-gap deployments, multi-cloud architecture, and enterprise-grade security hardening across AWS, Azure, and Google Cloud Platform.

---

## 🏗️ Architecture Overview

### **Deployment Topology**

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Scorpius Enterprise Platform                     │
├─────────────────────────────────────────────────────────────────────┤
│  🌐 Load Balancer    │  🔒 WAF/DDoS      │  📊 CDN               │
│  (ALB/ELB/NLB)      │  Protection        │  (CloudFront/etc)     │
├─────────────────────────────────────────────────────────────────────┤
│  🎛️  Kubernetes Cluster (EKS/GKE/AKS)                             │
│  ┌─────────────────┬─────────────────┬─────────────────────────────┐ │
│  │ 🛡️ Wallet Guard  │ 🔐 Auth Proxy   │ 📊 Usage Metering       │ │
│  │ (Port 8000)     │ (Port 8001)     │ (Port 8002)             │ │
│  ├─────────────────┼─────────────────┼─────────────────────────────┤ │
│  │ 📋 Audit Trail  │ 📑 Reporting    │ 🌐 Web Dashboard        │ │
│  │ (Port 8003)     │ (Port 8007)     │ (Port 3000)             │ │
│  └─────────────────┴─────────────────┴─────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────┤
│  🗄️ Data Layer                                                     │
│  ┌─────────────────┬─────────────────┬─────────────────────────────┐ │
│  │ 🐘 PostgreSQL   │ 🚀 Redis Cache  │ 🌩️ AWS QLDB             │ │
│  │ (RDS/CloudSQL)  │ (ElastiCache)   │ (Audit Ledger)          │ │
│  └─────────────────┴─────────────────┴─────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────┤
│  📊 Monitoring & Observability                                     │
│  ┌─────────────────┬─────────────────┬─────────────────────────────┐ │
│  │ 📈 Prometheus   │ 📊 Grafana      │ 🔍 Elasticsearch/ELK    │ │
│  │ (Metrics)       │ (Dashboards)    │ (Logging)               │ │
│  └─────────────────┴─────────────────┴─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Prerequisites

### **Infrastructure Requirements**

#### **Compute Resources**
- **Minimum**: 12 vCPUs, 32GB RAM, 500GB SSD
- **Recommended**: 24 vCPUs, 64GB RAM, 1TB NVMe SSD
- **Production**: 48 vCPUs, 128GB RAM, 2TB NVMe SSD

#### **Network Requirements**
- **VPC/VNET**: Dedicated virtual network with subnets
- **Load Balancer**: Application load balancer with SSL termination
- **NAT Gateway**: For outbound internet access (if required)
- **VPN/Direct Connect**: For on-premises connectivity

#### **Storage Requirements**
- **Database**: 1TB minimum, automated backups enabled
- **Object Storage**: 5TB minimum for reports and audit logs
- **Persistent Volumes**: 500GB for application data

### **Software Prerequisites**

#### **Container Runtime**
```bash
# Docker (minimum version 20.10)
docker --version
# Docker version 20.10.17

# Kubernetes (minimum version 1.24)
kubectl version --client
# Client Version: v1.27.3
```

#### **Infrastructure Tools**
```bash
# Terraform (minimum version 1.5)
terraform --version
# Terraform v1.5.2

# Helm (minimum version 3.12)
helm version
# Version: v3.12.1
```

---

## ☁️ Cloud-Specific Deployment

### **Amazon Web Services (AWS)**

#### **1. Infrastructure Setup with Terraform**

```bash
# Clone deployment repository
git clone https://github.com/scorpius-enterprise/deploy-aws.git
cd deploy-aws

# Configure AWS credentials
aws configure
# AWS Access Key ID: AKIA...
# AWS Secret Access Key: ...
# Default region name: us-west-2

# Initialize Terraform
terraform init

# Plan deployment
terraform plan -var-file="production.tfvars"

# Apply infrastructure
terraform apply -var-file="production.tfvars"
```

**production.tfvars:**
```hcl
# AWS Configuration
aws_region = "us-west-2"
availability_zones = ["us-west-2a", "us-west-2b", "us-west-2c"]

# Cluster Configuration
cluster_name = "scorpius-enterprise"
cluster_version = "1.27"
node_instance_type = "m5.2xlarge"
node_desired_capacity = 6
node_max_capacity = 12

# Database Configuration
db_instance_class = "db.r6g.xlarge"
db_allocated_storage = 1000
db_backup_retention = 30

# Security Configuration
vpc_cidr = "10.0.0.0/16"
enable_private_subnets = true
enable_nat_gateway = true
enable_vpn_gateway = true

# Monitoring
enable_prometheus = true
enable_grafana = true
enable_elasticsearch = true
```

#### **2. EKS Cluster Deployment**

```bash
# Update kubeconfig
aws eks update-kubeconfig --region us-west-2 --name scorpius-enterprise

# Verify cluster access
kubectl get nodes
# NAME                                       STATUS   ROLES    AGE   VERSION
# ip-10-0-1-123.us-west-2.compute.internal   Ready    <none>   5m    v1.27.3

# Install AWS Load Balancer Controller
helm repo add eks https://aws.github.io/eks-charts
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \\
  --set clusterName=scorpius-enterprise \\
  --set serviceAccount.create=false \\
  --set serviceAccount.name=aws-load-balancer-controller
```

#### **3. Database Setup**

```bash
# Create RDS PostgreSQL instance
aws rds create-db-instance \\
  --db-instance-identifier scorpius-production \\
  --db-instance-class db.r6g.xlarge \\
  --engine postgres \\
  --engine-version 15.3 \\
  --allocated-storage 1000 \\
  --storage-type gp3 \\
  --db-name scorpius \\
  --master-username scorpius_admin \\
  --master-user-password "${DB_PASSWORD}" \\
  --vpc-security-group-ids sg-abc123 \\
  --db-subnet-group-name scorpius-db-subnet \\
  --backup-retention-period 30 \\
  --storage-encrypted \\
  --kms-key-id arn:aws:kms:us-west-2:123456789012:key/abc-123

# Create ElastiCache Redis cluster
aws elasticache create-cache-cluster \\
  --cache-cluster-id scorpius-redis \\
  --cache-node-type cache.r6g.xlarge \\
  --engine redis \\
  --engine-version 7.0 \\
  --num-cache-nodes 3 \\
  --security-group-ids sg-def456 \\
  --subnet-group-name scorpius-cache-subnet
```

### **Microsoft Azure (AKS)**

#### **1. Infrastructure Setup**

```bash
# Login to Azure
az login

# Create resource group
az group create --name scorpius-enterprise --location eastus

# Create AKS cluster
az aks create \\
  --resource-group scorpius-enterprise \\
  --name scorpius-cluster \\
  --node-count 6 \\
  --node-vm-size Standard_D4s_v3 \\
  --kubernetes-version 1.27.3 \\
  --enable-addons monitoring \\
  --enable-managed-identity \\
  --network-plugin azure \\
  --network-policy azure

# Get credentials
az aks get-credentials --resource-group scorpius-enterprise --name scorpius-cluster
```

#### **2. Azure Database Setup**

```bash
# Create PostgreSQL server
az postgres flexible-server create \\
  --resource-group scorpius-enterprise \\
  --name scorpius-db \\
  --location eastus \\
  --admin-user scorpius_admin \\
  --admin-password "${DB_PASSWORD}" \\
  --sku-name Standard_D4s_v3 \\
  --tier GeneralPurpose \\
  --storage-size 1024 \\
  --version 15

# Create Redis cache
az redis create \\
  --resource-group scorpius-enterprise \\
  --name scorpius-cache \\
  --location eastus \\
  --sku Premium \\
  --vm-size P3
```

### **Google Cloud Platform (GKE)**

#### **1. Infrastructure Setup**

```bash
# Set project and region
gcloud config set project scorpius-enterprise
gcloud config set compute/region us-central1

# Create GKE cluster
gcloud container clusters create scorpius-cluster \\
  --region=us-central1 \\
  --machine-type=e2-standard-4 \\
  --num-nodes=6 \\
  --enable-autoscaling \\
  --min-nodes=3 \\
  --max-nodes=12 \\
  --enable-autorepair \\
  --enable-autoupgrade \\
  --enable-ip-alias \\
  --network=scorpius-vpc \\
  --subnetwork=scorpius-subnet

# Get credentials
gcloud container clusters get-credentials scorpius-cluster --region=us-central1
```

#### **2. Google Cloud Database Setup**

```bash
# Create Cloud SQL PostgreSQL instance
gcloud sql instances create scorpius-db \\
  --database-version=POSTGRES_15 \\
  --tier=db-custom-4-16384 \\
  --region=us-central1 \\
  --storage-type=SSD \\
  --storage-size=1000GB \\
  --backup-start-time=03:00 \\
  --enable-bin-log \\
  --deletion-protection

# Create Memorystore Redis instance
gcloud redis instances create scorpius-cache \\
  --size=10 \\
  --region=us-central1 \\
  --redis-version=redis_7_0
```

---

## 🎛️ Kubernetes Deployment

### **1. Namespace and RBAC Setup**

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: scorpius-enterprise
  labels:
    name: scorpius-enterprise
    environment: production
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: scorpius-service-account
  namespace: scorpius-enterprise
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: scorpius-cluster-role
rules:
- apiGroups: [""]
  resources: ["pods", "services", "endpoints"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["apps"]
  resources: ["deployments", "replicasets"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: scorpius-cluster-role-binding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: scorpius-cluster-role
subjects:
- kind: ServiceAccount
  name: scorpius-service-account
  namespace: scorpius-enterprise
```

### **2. ConfigMaps and Secrets**

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: scorpius-config
  namespace: scorpius-enterprise
data:
  ENVIRONMENT: "production"
  LOG_LEVEL: "INFO"
  PROMETHEUS_ENABLED: "true"
  REDIS_URL: "redis://scorpius-cache:6379/0"
  CORS_ORIGINS: "https://app.company.com"
---
apiVersion: v1
kind: Secret
metadata:
  name: scorpius-secrets
  namespace: scorpius-enterprise
type: Opaque
data:
  DATABASE_URL: cG9zdGdyZXNxbDovL3Njb3JwaXVzOi4uLg==  # base64 encoded
  SECRET_KEY: c2VjcmV0X2tleV9oZXJl  # base64 encoded
  AWS_ACCESS_KEY_ID: QUtJQS4uLg==  # base64 encoded
  AWS_SECRET_ACCESS_KEY: c2VjcmV0X2FjY2Vzc19rZXk=  # base64 encoded
```

### **3. Application Deployment**

```yaml
# wallet-guard-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: wallet-guard
  namespace: scorpius-enterprise
  labels:
    app: wallet-guard
spec:
  replicas: 3
  selector:
    matchLabels:
      app: wallet-guard
  template:
    metadata:
      labels:
        app: wallet-guard
    spec:
      serviceAccountName: scorpius-service-account
      containers:
      - name: wallet-guard
        image: scorpius/wallet-guard:1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: scorpius-secrets
              key: DATABASE_URL
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: scorpius-config
              key: REDIS_URL
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        securityContext:
          runAsNonRoot: true
          runAsUser: 1000
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
```

### **4. Services and Ingress**

```yaml
# services.yaml
apiVersion: v1
kind: Service
metadata:
  name: wallet-guard-service
  namespace: scorpius-enterprise
spec:
  selector:
    app: wallet-guard
  ports:
  - protocol: TCP
    port: 8000
    targetPort: 8000
  type: ClusterIP
---
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: scorpius-ingress
  namespace: scorpius-enterprise
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:us-west-2:123456789012:certificate/abc-123
    alb.ingress.kubernetes.io/ssl-policy: ELBSecurityPolicy-TLS-1-2-2017-01
spec:
  tls:
  - hosts:
    - api.scorpius.company.com
  rules:
  - host: api.scorpius.company.com
    http:
      paths:
      - path: /v1/wallets
        pathType: Prefix
        backend:
          service:
            name: wallet-guard-service
            port:
              number: 8000
```

---

## 🔒 Security Hardening

### **1. Network Security**

#### **Network Policies**
```yaml
# network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: scorpius-network-policy
  namespace: scorpius-enterprise
spec:
  podSelector:
    matchLabels:
      app: wallet-guard
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - protocol: TCP
      port: 5432  # PostgreSQL
  - to: []
    ports:
    - protocol: TCP
      port: 443  # HTTPS
    - protocol: TCP
      port: 53   # DNS
    - protocol: UDP
      port: 53   # DNS
```

### **2. Pod Security Standards**

```yaml
# pod-security-policy.yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: scorpius-restricted
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  hostNetwork: false
  hostIPC: false
  hostPID: false
  runAsUser:
    rule: 'MustRunAsNonRoot'
  supplementalGroups:
    rule: 'MustRunAs'
    ranges:
      - min: 1
        max: 65535
  fsGroup:
    rule: 'MustRunAs'
    ranges:
      - min: 1
        max: 65535
  readOnlyRootFilesystem: true
```

### **3. RBAC Configuration**

```yaml
# rbac.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: scorpius-enterprise
  name: scorpius-pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]
- apiGroups: [""]
  resources: ["configmaps", "secrets"]
  verbs: ["get"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: scorpius-pod-reader-binding
  namespace: scorpius-enterprise
subjects:
- kind: ServiceAccount
  name: scorpius-service-account
  namespace: scorpius-enterprise
roleRef:
  kind: Role
  name: scorpius-pod-reader
  apiGroup: rbac.authorization.k8s.io
```

---

## 📊 Monitoring & Observability

### **1. Prometheus Setup**

```yaml
# prometheus-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: scorpius-enterprise
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s
    
    rule_files:
      - "/etc/prometheus/rules/*.yml"
    
    scrape_configs:
      - job_name: 'kubernetes-pods'
        kubernetes_sd_configs:
        - role: pod
        relabel_configs:
        - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
          action: keep
          regex: true
        - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
          action: replace
          target_label: __metrics_path__
          regex: (.+)
        - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
          action: replace
          regex: ([^:]+)(?::\\d+)?;(\\d+)
          replacement: $1:$2
          target_label: __address__
        - action: labelmap
          regex: __meta_kubernetes_pod_label_(.+)
        - source_labels: [__meta_kubernetes_namespace]
          action: replace
          target_label: kubernetes_namespace
        - source_labels: [__meta_kubernetes_pod_name]
          action: replace
          target_label: kubernetes_pod_name
```

### **2. Grafana Dashboards**

```yaml
# grafana-dashboard.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: scorpius-dashboard
  namespace: scorpius-enterprise
  labels:
    grafana_dashboard: "1"
data:
  scorpius-overview.json: |
    {
      "dashboard": {
        "id": null,
        "title": "Scorpius Enterprise Overview",
        "tags": ["scorpius", "enterprise"],
        "timezone": "browser",
        "panels": [
          {
            "id": 1,
            "title": "API Request Rate",
            "type": "graph",
            "targets": [
              {
                "expr": "rate(http_requests_total{job='wallet-guard'}[5m])",
                "legendFormat": "Requests/sec"
              }
            ]
          },
          {
            "id": 2,
            "title": "Wallets Protected",
            "type": "stat",
            "targets": [
              {
                "expr": "wallets_protected_total",
                "legendFormat": "Total Wallets"
              }
            ]
          }
        ]
      }
    }
```

---

## 🔄 Backup & Disaster Recovery

### **1. Database Backup Strategy**

```bash
#!/bin/bash
# backup-script.sh

# Set variables
BACKUP_DIR="/backups/scorpius"
DB_HOST="scorpius-db.cluster-abc123.us-west-2.rds.amazonaws.com"
DB_NAME="scorpius"
DB_USER="scorpius_admin"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
S3_BUCKET="scorpius-enterprise-backups"

# Create backup directory
mkdir -p ${BACKUP_DIR}

# Perform database backup
pg_dump -h ${DB_HOST} -U ${DB_USER} -d ${DB_NAME} \\
  --verbose --clean --no-owner --no-privileges \\
  --format=custom \\
  --file=${BACKUP_DIR}/scorpius_${TIMESTAMP}.backup

# Compress backup
gzip ${BACKUP_DIR}/scorpius_${TIMESTAMP}.backup

# Upload to S3
aws s3 cp ${BACKUP_DIR}/scorpius_${TIMESTAMP}.backup.gz \\
  s3://${S3_BUCKET}/database/scorpius_${TIMESTAMP}.backup.gz

# Cleanup local backups older than 7 days
find ${BACKUP_DIR} -name "*.backup.gz" -mtime +7 -delete

# Send notification
echo "Database backup completed: scorpius_${TIMESTAMP}.backup.gz" | \\
  mail -s "Scorpius Backup Success" admin@company.com
```

### **2. Application State Backup**

```yaml
# velero-backup.yaml
apiVersion: velero.io/v1
kind: Backup
metadata:
  name: scorpius-daily-backup
  namespace: velero
spec:
  includedNamespaces:
  - scorpius-enterprise
  excludedResources:
  - pods
  - events
  ttl: 720h0m0s  # 30 days
  storageLocation: aws-s3
  volumeSnapshotLocations:
  - aws-ebs
---
apiVersion: velero.io/v1
kind: Schedule
metadata:
  name: scorpius-daily-schedule
  namespace: velero
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  template:
    includedNamespaces:
    - scorpius-enterprise
    ttl: 720h0m0s
```

### **3. Disaster Recovery Plan**

#### **Recovery Time Objectives (RTO)**
- **Database Recovery**: < 4 hours
- **Application Recovery**: < 2 hours
- **Full Service Restoration**: < 6 hours

#### **Recovery Point Objectives (RPO)**
- **Database**: < 15 minutes (continuous backup)
- **Application State**: < 1 hour (hourly snapshots)
- **Configuration**: < 5 minutes (GitOps)

---

## 🎛️ Operational Procedures

### **1. Health Checks**

```bash
# health-check.sh
#!/bin/bash

# Check all service endpoints
SERVICES=(
  "wallet-guard:8000"
  "auth-proxy:8001"
  "usage-metering:8002"
  "audit-trail:8003"
  "reporting:8007"
)

for service in "${SERVICES[@]}"; do
  IFS=':' read -r name port <<< "$service"
  
  if curl -f "http://${name}.scorpius-enterprise.svc.cluster.local:${port}/health" &>/dev/null; then
    echo "✅ ${name} is healthy"
  else
    echo "❌ ${name} is unhealthy"
    kubectl logs -n scorpius-enterprise deployment/${name} --tail=50
  fi
done

# Check database connectivity
if pg_isready -h $DB_HOST -p 5432 -U $DB_USER; then
  echo "✅ Database is available"
else
  echo "❌ Database is unavailable"
fi

# Check Redis connectivity
if redis-cli -h $REDIS_HOST ping | grep -q PONG; then
  echo "✅ Redis is available"
else
  echo "❌ Redis is unavailable"
fi
```

### **2. Scaling Procedures**

```bash
# scale-services.sh
#!/bin/bash

# Scale wallet-guard for high load
kubectl scale deployment wallet-guard -n scorpius-enterprise --replicas=6

# Scale auth-proxy for authentication load
kubectl scale deployment auth-proxy -n scorpius-enterprise --replicas=4

# Scale reporting service for report generation
kubectl scale deployment reporting -n scorpius-enterprise --replicas=3

# Enable horizontal pod autoscaler
kubectl autoscale deployment wallet-guard -n scorpius-enterprise \\
  --cpu-percent=70 --min=3 --max=10

echo "Services scaled successfully"
```

---

## 📞 Support & Troubleshooting

### **Common Issues**

#### **Database Connection Issues**
```bash
# Check database connectivity
kubectl exec -it deployment/wallet-guard -n scorpius-enterprise -- \\
  psql $DATABASE_URL -c "SELECT 1;"

# Check database logs
kubectl logs -n scorpius-enterprise deployment/wallet-guard --previous
```

#### **Certificate Issues**
```bash
# Check certificate expiry
openssl x509 -in /etc/ssl/certs/scorpius.crt -text -noout | grep "Not After"

# Renew Let's Encrypt certificate
certbot renew --dry-run
```

#### **Performance Issues**
```bash
# Check resource usage
kubectl top pods -n scorpius-enterprise
kubectl top nodes

# Check for OOMKilled pods
kubectl get events -n scorpius-enterprise --field-selector reason=OOMKilling
```

### **Emergency Contacts**

- **24/7 Support**: [support@scorpius.com](mailto:support@scorpius.com)
- **DevOps Team**: [devops@scorpius.com](mailto:devops@scorpius.com)
- **Emergency Hotline**: +1-800-SCORPIUS
- **Slack Channel**: #scorpius-production

---

## 📋 Deployment Checklist

### **Pre-Deployment**
- [ ] Infrastructure provisioned and tested
- [ ] Security groups and network policies configured
- [ ] Database instances created and configured
- [ ] SSL certificates generated and deployed
- [ ] Monitoring and logging infrastructure ready
- [ ] Backup systems configured and tested

### **Deployment**
- [ ] Kubernetes cluster operational
- [ ] All application services deployed
- [ ] Database migrations completed
- [ ] Configuration and secrets applied
- [ ] Ingress and load balancers configured
- [ ] Health checks passing

### **Post-Deployment**
- [ ] End-to-end testing completed
- [ ] Monitoring dashboards configured
- [ ] Alerting rules activated
- [ ] Backup verification completed
- [ ] Documentation updated
- [ ] Team trained on operational procedures

---

*This deployment guide is maintained by the Scorpius DevOps team and updated with each platform release. For the latest information and support, contact [devops@scorpius.com](mailto:devops@scorpius.com).*
