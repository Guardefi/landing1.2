terraform {
  required_version = ">= 1.3"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

################################################################################
# VPC (using community module)
################################################################################
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.1.2"

  name = "${var.project}-vpc"
  cidr = var.vpc_cidr

  azs             = slice(data.aws_availability_zones.available.names, 0, 3)
  public_subnets  = [for i, az in azs : cidrsubnet(var.vpc_cidr, 8, i)]
  private_subnets = [for i, az in azs : cidrsubnet(var.vpc_cidr, 8, i + 10)]

  enable_nat_gateway = true
  single_nat_gateway = true
  enable_dns_hostnames = true
}

################################################################################
# RDS (PostgreSQL)
################################################################################
module "rds" {
  source  = "terraform-aws-modules/rds/aws"
  version = "6.5.4"

  identifier = "${var.project}-db"

  engine            = "postgres"
  engine_version    = var.db_engine_version
  instance_class    = var.db_instance_class
  allocated_storage = 20

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  vpc_security_group_ids = [module.vpc.default_security_group_id]
  subnet_ids             = module.vpc.private_subnets

  publicly_accessible = false
  skip_final_snapshot = true
}

################################################################################
# ElastiCache (Redis)
################################################################################
module "elasticache" {
  source  = "terraform-aws-modules/elasticache/aws"
  version = "5.4.0"

  name                = "${var.project}-redis"
  engine              = "redis"
  engine_version      = var.redis_engine_version
  node_type           = var.redis_node_type
  number_cache_clusters = 1

  vpc_id              = module.vpc.vpc_id
  subnets             = module.vpc.private_subnets
}

################################################################################
# ACM + ALB
################################################################################
resource "aws_acm_certificate" "this" {
  domain_name       = var.domain_name
  validation_method = "DNS"
}

module "alb" {
  source  = "terraform-aws-modules/alb/aws"
  version = "9.7.0"

  name = "${var.project}-alb"

  vpc_id  = module.vpc.vpc_id
  subnets = module.vpc.public_subnets

  enable_http2                 = true
  ip_address_type              = "ipv4"

  listeners = {
    http = {
      port     = 80
      protocol = "HTTP"
      action_type = "redirect"
      redirect = {
        port        = "443"
        protocol    = "HTTPS"
        status_code = "HTTP_301"
      }
    }
    https = {
      port            = 443
      protocol        = "HTTPS"
      ssl_policy      = "ELBSecurityPolicy-TLS13-1-2-2021-06"
      certificate_arn = aws_acm_certificate.this.arn
      action_type     = "fixed-response"
      fixed_response = {
        content_type = "text/plain"
        message_body = "placeholder"
        status_code  = 200
      }
    }
  }
}

################################################################################
# EKS Cluster
################################################################################
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "20.8.4"

  cluster_name    = "${var.project}-eks"
  cluster_version = var.k8s_version

  subnet_ids   = module.vpc.private_subnets
  vpc_id       = module.vpc.vpc_id

  node_groups = {
    default = {
      desired_capacity = 2
      max_capacity     = 3
      min_capacity     = 1

      instance_type = var.worker_instance_type
    }
  }
} 