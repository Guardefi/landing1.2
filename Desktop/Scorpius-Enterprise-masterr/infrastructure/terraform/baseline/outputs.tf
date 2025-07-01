output "vpc_id" {
  value = module.vpc.vpc_id
}

output "private_subnet_ids" {
  value = module.vpc.private_subnets
}

output "db_endpoint" {
  value = module.rds.db_instance_endpoint
}

output "db_username" {
  value = var.db_username
}

output "redis_endpoint" {
  value = module.elasticache.primary_endpoint_address
}

output "eks_cluster_name" {
  value = module.eks.cluster_name
}

output "eks_cluster_endpoint" {
  value = module.eks.cluster_endpoint
}

output "alb_dns_name" {
  value = module.alb.this_lb_dns_name
} 