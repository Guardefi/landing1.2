# Scorpius Enterprise Platform - EKS Deployment
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11"
    }
  }

  backend "s3" {
    # Configure this for your environment
    bucket         = var.terraform_state_bucket
    key            = "scorpius/terraform.tfstate"
    region         = var.aws_region
    encrypt        = true
    dynamodb_table = var.terraform_lock_table
  }
}

# Configure the AWS Provider
provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Environment   = var.environment
      Project       = "scorpius-enterprise"
      ManagedBy     = "terraform"
      Owner         = var.owner
      CostCenter    = var.cost_center
    }
  }
}

# Data sources
data "aws_availability_zones" "available" {
  filter {
    name   = "opt-in-status"
    values = ["opt-in-not-required"]
  }
}

data "aws_caller_identity" "current" {}

# Local values
locals {
  name            = "${var.project_name}-${var.environment}"
  cluster_version = var.kubernetes_version
  
  azs = slice(data.aws_availability_zones.available.names, 0, 3)
  
  tags = {
    Environment = var.environment
    Project     = var.project_name
    ClusterName = local.name
  }
}

################################################################################
# VPC
################################################################################

module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "${local.name}-vpc"
  cidr = var.vpc_cidr

  azs             = local.azs
  private_subnets = var.private_subnets
  public_subnets  = var.public_subnets
  
  enable_nat_gateway = true
  enable_vpn_gateway = false
  enable_dns_hostnames = true
  enable_dns_support = true

  # EKS requirements
  public_subnet_tags = {
    "kubernetes.io/role/elb" = 1
  }

  private_subnet_tags = {
    "kubernetes.io/role/internal-elb" = 1
  }

  tags = local.tags
}

################################################################################
# EKS Cluster
################################################################################

module "eks" {
  source = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = local.name
  cluster_version = local.cluster_version

  vpc_id                         = module.vpc.vpc_id
  subnet_ids                     = module.vpc.private_subnets
  cluster_endpoint_public_access = var.cluster_endpoint_public_access

  # EKS Managed Node Groups
  eks_managed_node_groups = {
    # System nodes for platform services
    system = {
      name = "${local.name}-system"
      
      instance_types = ["t3.large"]
      min_size       = 2
      max_size       = 4
      desired_size   = 2

      k8s_labels = {
        Environment = var.environment
        NodeType    = "system"
      }
      
      taints = {
        dedicated = {
          key    = "system"
          value  = "true"
          effect = "NO_SCHEDULE"
        }
      }
    }

    # Application nodes for workloads
    application = {
      name = "${local.name}-application"
      
      instance_types = ["c5.xlarge"]
      min_size       = 3
      max_size       = 10
      desired_size   = 3

      k8s_labels = {
        Environment = var.environment
        NodeType    = "application"
      }
    }

    # High-memory nodes for scanning workloads
    scanner = {
      name = "${local.name}-scanner"
      
      instance_types = ["r5.2xlarge"]
      min_size       = 2
      max_size       = 8
      desired_size   = 2

      k8s_labels = {
        Environment = var.environment
        NodeType    = "scanner"
      }
      
      taints = {
        dedicated = {
          key    = "scanner"
          value  = "true"
          effect = "NO_SCHEDULE"
        }
      }
    }
  }

  # OIDC Identity provider
  cluster_identity_providers = {
    sts = {
      client_id = "sts.amazonaws.com"
    }
  }

  tags = local.tags
}

################################################################################
# EKS Add-ons
################################################################################

resource "aws_eks_addon" "addons" {
  for_each = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent = true
    }
    aws-ebs-csi-driver = {
      most_recent = true
    }
  }

  cluster_name             = module.eks.cluster_name
  addon_name               = each.key
  addon_version            = each.value.most_recent ? null : each.value.version
  resolve_conflicts        = "OVERWRITE"
  preserve                 = true
  
  depends_on = [module.eks]
}

################################################################################
# RDS (PostgreSQL)
################################################################################

module "rds" {
  source = "terraform-aws-modules/rds/aws"
  version = "~> 6.0"

  identifier = "${local.name}-postgres"

  engine            = "postgres"
  engine_version    = var.postgres_version
  family            = "postgres15"
  major_engine_version = "15"
  instance_class    = var.rds_instance_class

  allocated_storage     = var.rds_allocated_storage
  max_allocated_storage = var.rds_max_allocated_storage
  storage_encrypted     = true

  db_name  = var.database_name
  username = var.database_username
  password = random_password.database_password.result
  port     = 5432

  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = module.vpc.database_subnet_group

  maintenance_window = "Mon:00:00-Mon:03:00"
  backup_window      = "03:00-06:00"
  
  backup_retention_period = var.backup_retention_period
  skip_final_snapshot     = var.environment != "production"
  deletion_protection     = var.environment == "production"

  performance_insights_enabled = true
  performance_insights_retention_period = 7

  create_monitoring_role = true
  monitoring_interval    = 60

  tags = local.tags
}

# RDS Security Group
resource "aws_security_group" "rds" {
  name        = "${local.name}-rds-sg"
  description = "Security group for RDS database"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
    description = "PostgreSQL access from VPC"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = merge(local.tags, {
    Name = "${local.name}-rds-sg"
  })
}

# Database password
resource "random_password" "database_password" {
  length  = 32
  special = true
}

################################################################################
# ElastiCache (Redis)
################################################################################

module "redis" {
  source = "terraform-aws-modules/elasticache/aws"
  version = "~> 1.0"

  cluster_id = "${local.name}-redis"
  
  engine               = "redis"
  engine_version       = var.redis_version
  node_type            = var.redis_node_type
  num_cache_nodes      = var.redis_num_nodes
  parameter_group_name = "default.redis7"
  port                 = 6379

  subnet_group_name = module.vpc.elasticache_subnet_group_name
  security_group_ids = [aws_security_group.redis.id]

  at_rest_encryption_enabled = true
  transit_encryption_enabled = false  # Disable for compatibility
  auth_token_enabled         = false  # Disable for compatibility

  maintenance_window = "sun:05:00-sun:09:00"
  snapshot_window    = "01:00-05:00"
  snapshot_retention_limit = 5

  tags = local.tags
}

# Redis Security Group
resource "aws_security_group" "redis" {
  name        = "${local.name}-redis-sg"
  description = "Security group for Redis cluster"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
    description = "Redis access from VPC"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = merge(local.tags, {
    Name = "${local.name}-redis-sg"
  })
}

################################################################################
# QLDB for Audit Trail
################################################################################

resource "aws_qldb_ledger" "audit_trail" {
  name             = "${local.name}-audit-trail"
  permissions_mode = "STANDARD"
  
  deletion_protection = var.environment == "production"

  tags = local.tags
}

################################################################################
# Application Load Balancer
################################################################################

module "alb" {
  source = "terraform-aws-modules/alb/aws"
  version = "~> 8.0"

  name = "${local.name}-alb"

  load_balancer_type = "application"

  vpc_id             = module.vpc.vpc_id
  subnets            = module.vpc.public_subnets
  security_groups    = [aws_security_group.alb.id]

  target_groups = [
    {
      name             = "${local.name}-api-gateway"
      backend_protocol = "HTTP"
      backend_port     = 8000
      target_type      = "ip"
      
      health_check = {
        enabled             = true
        healthy_threshold   = 2
        interval            = 30
        matcher             = "200"
        path                = "/health"
        port                = "traffic-port"
        protocol            = "HTTP"
        timeout             = 5
        unhealthy_threshold = 2
      }
    }
  ]

  https_listeners = [
    {
      port               = 443
      protocol           = "HTTPS"
      certificate_arn    = aws_acm_certificate_validation.this.certificate_arn
      target_group_index = 0
    }
  ]

  http_tcp_listeners = [
    {
      port        = 80
      protocol    = "HTTP"
      action_type = "redirect"
      redirect = {
        port        = "443"
        protocol    = "HTTPS"
        status_code = "HTTP_301"
      }
    }
  ]

  tags = local.tags
}

# ALB Security Group
resource "aws_security_group" "alb" {
  name        = "${local.name}-alb-sg"
  description = "Security group for Application Load Balancer"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP"
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = merge(local.tags, {
    Name = "${local.name}-alb-sg"
  })
}

################################################################################
# TLS Certificate
################################################################################

# ACM Certificate
resource "aws_acm_certificate" "this" {
  domain_name       = var.domain_name
  subject_alternative_names = [
    "*.${var.domain_name}"
  ]
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  tags = local.tags
}

# Certificate validation
resource "aws_acm_certificate_validation" "this" {
  certificate_arn         = aws_acm_certificate.this.arn
  validation_record_fqdns = [for record in aws_route53_record.validation : record.fqdn]
}

# Route53 validation records
resource "aws_route53_record" "validation" {
  for_each = {
    for dvo in aws_acm_certificate.this.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = data.aws_route53_zone.this.zone_id
}

data "aws_route53_zone" "this" {
  name         = var.domain_name
  private_zone = false
}

################################################################################
# CloudWatch Log Groups
################################################################################

resource "aws_cloudwatch_log_group" "eks_cluster" {
  name              = "/aws/eks/${local.name}/cluster"
  retention_in_days = var.log_retention_days

  tags = local.tags
}

resource "aws_cloudwatch_log_group" "application_logs" {
  name              = "/aws/scorpius/${var.environment}/application"
  retention_in_days = var.log_retention_days

  tags = local.tags
}
