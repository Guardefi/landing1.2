# Scorpius Enterprise Platform - EKS Outputs

# VPC Outputs
output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.vpc_id
}

output "vpc_cidr_block" {
  description = "CIDR block of the VPC"
  value       = module.vpc.vpc_cidr_block
}

output "private_subnets" {
  description = "List of IDs of private subnets"
  value       = module.vpc.private_subnets
}

output "public_subnets" {
  description = "List of IDs of public subnets"
  value       = module.vpc.public_subnets
}

# EKS Outputs
output "cluster_id" {
  description = "EKS cluster ID"
  value       = module.eks.cluster_id
}

output "cluster_arn" {
  description = "EKS cluster ARN"
  value       = module.eks.cluster_arn
}

output "cluster_endpoint" {
  description = "Endpoint for EKS control plane"
  value       = module.eks.cluster_endpoint
}

output "cluster_security_group_id" {
  description = "Security group ID attached to the EKS cluster"
  value       = module.eks.cluster_security_group_id
}

output "cluster_iam_role_name" {
  description = "IAM role name associated with EKS cluster"
  value       = module.eks.cluster_iam_role_name
}

output "cluster_iam_role_arn" {
  description = "IAM role ARN associated with EKS cluster"
  value       = module.eks.cluster_iam_role_arn
}

output "cluster_certificate_authority_data" {
  description = "Base64 encoded certificate data required to communicate with the cluster"
  value       = module.eks.cluster_certificate_authority_data
}

output "cluster_primary_security_group_id" {
  description = "Cluster security group that was created by Amazon EKS for the cluster"
  value       = module.eks.cluster_primary_security_group_id
}

output "oidc_provider_arn" {
  description = "The ARN of the OIDC Provider if enabled"
  value       = module.eks.oidc_provider_arn
}

# Node Groups
output "eks_managed_node_groups" {
  description = "Map of attribute maps for all EKS managed node groups created"
  value       = module.eks.eks_managed_node_groups
}

# RDS Outputs
output "rds_cluster_endpoint" {
  description = "RDS cluster endpoint"
  value       = aws_rds_cluster.main.endpoint
}

output "rds_cluster_reader_endpoint" {
  description = "RDS cluster reader endpoint"
  value       = aws_rds_cluster.main.reader_endpoint
}

output "rds_cluster_id" {
  description = "RDS cluster identifier"
  value       = aws_rds_cluster.main.cluster_identifier
}

output "rds_cluster_arn" {
  description = "RDS cluster ARN"
  value       = aws_rds_cluster.main.arn
}

output "rds_cluster_database_name" {
  description = "RDS cluster database name"
  value       = aws_rds_cluster.main.database_name
}

output "rds_cluster_port" {
  description = "RDS cluster port"
  value       = aws_rds_cluster.main.port
}

# ElastiCache Redis Outputs
output "redis_cluster_id" {
  description = "ElastiCache Redis cluster ID"
  value       = aws_elasticache_replication_group.redis.id
}

output "redis_primary_endpoint" {
  description = "ElastiCache Redis primary endpoint"
  value       = aws_elasticache_replication_group.redis.primary_endpoint_address
}

output "redis_reader_endpoint" {
  description = "ElastiCache Redis reader endpoint"
  value       = aws_elasticache_replication_group.redis.reader_endpoint_address
}

output "redis_port" {
  description = "ElastiCache Redis port"
  value       = aws_elasticache_replication_group.redis.port
}

# QLDB Outputs
output "qldb_ledger_name" {
  description = "QLDB ledger name"
  value       = aws_qldb_ledger.audit_ledger.name
}

output "qldb_ledger_arn" {
  description = "QLDB ledger ARN"
  value       = aws_qldb_ledger.audit_ledger.arn
}

# Load Balancer Outputs
output "load_balancer_dns_name" {
  description = "DNS name of the load balancer"
  value       = aws_lb.main.dns_name
}

output "load_balancer_zone_id" {
  description = "Hosted zone ID of the load balancer"
  value       = aws_lb.main.zone_id
}

output "load_balancer_arn" {
  description = "ARN of the load balancer"
  value       = aws_lb.main.arn
}

# Certificate Outputs
output "acm_certificate_arn" {
  description = "ARN of the ACM certificate"
  value       = aws_acm_certificate.main.arn
}

output "acm_certificate_domain_validation_options" {
  description = "Domain validation options for the ACM certificate"
  value       = aws_acm_certificate.main.domain_validation_options
}

# CloudWatch Outputs
output "log_group_name" {
  description = "CloudWatch log group name"
  value       = aws_cloudwatch_log_group.cluster.name
}

output "log_group_arn" {
  description = "CloudWatch log group ARN"
  value       = aws_cloudwatch_log_group.cluster.arn
}

# Security Groups
output "rds_security_group_id" {
  description = "RDS security group ID"
  value       = aws_security_group.rds.id
}

output "redis_security_group_id" {
  description = "Redis security group ID"
  value       = aws_security_group.redis.id
}

output "alb_security_group_id" {
  description = "ALB security group ID"
  value       = aws_security_group.alb.id
}

# IAM Outputs
output "node_security_group_id" {
  description = "ID of the node shared security group"
  value       = module.eks.node_security_group_id
}

output "cluster_service_account_role_arn" {
  description = "ARN of the IAM role for cluster service account"
  value       = module.eks.cluster_iam_role_arn
}

# Kubernetes Configuration
output "kubectl_config" {
  description = "kubectl config as generated by the module"
  value = {
    cluster_name                     = module.eks.cluster_id
    endpoint                        = module.eks.cluster_endpoint
    certificate_authority_data      = module.eks.cluster_certificate_authority_data
    region                         = var.aws_region
  }
  sensitive = true
}

# Application URLs
output "application_urls" {
  description = "Application URLs"
  value = {
    api_url      = "https://${var.domain_name}/api"
    web_url      = "https://${var.domain_name}"
    metrics_url  = "https://${var.domain_name}/metrics"
    health_url   = "https://${var.domain_name}/health"
  }
}

# Connection Strings (Sensitive)
output "database_connection_string" {
  description = "Database connection string"
  value       = "postgresql://${aws_rds_cluster.main.master_username}:${random_password.rds_password.result}@${aws_rds_cluster.main.endpoint}:${aws_rds_cluster.main.port}/${aws_rds_cluster.main.database_name}"
  sensitive   = true
}

output "redis_connection_string" {
  description = "Redis connection string"
  value       = "redis://${aws_elasticache_replication_group.redis.primary_endpoint_address}:${aws_elasticache_replication_group.redis.port}"
  sensitive   = true
}

# Backup Information
output "backup_vault_arn" {
  description = "AWS Backup vault ARN"
  value       = aws_backup_vault.main.arn
}

output "backup_plan_arn" {
  description = "AWS Backup plan ARN"
  value       = aws_backup_plan.main.arn
}
