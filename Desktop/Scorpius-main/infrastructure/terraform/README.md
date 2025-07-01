# Scorpius Terraform Baseline

This folder contains Terraform code to provision the essential AWS infrastructure for the Scorpius Enterprise Platform.

Components provisioned:

1. **VPC** – three-AZ highly-available network with public/private subnets and NAT GW.
2. **EKS** – Kubernetes control-plane for microservices (Helm values can consume `eks_cluster_name`, `alb_dns_name`, etc.).
3. **RDS (PostgreSQL)** – managed database backend.
4. **ElastiCache (Redis)** – caching & Celery broker.
5. **ACM + ALB** – TLS termination and external load balancer.

## Usage

```bash
cd infrastructure/terraform/baseline
terraform init
terraform plan -var="project=scorpius" -var="db_password=$(openssl rand -base64 12)" -out=tfplan
terraform apply tfplan
```

Outputs can be fed into Helm charts via `terraform output -json > values.auto.tfvars.json` or a CI step. 