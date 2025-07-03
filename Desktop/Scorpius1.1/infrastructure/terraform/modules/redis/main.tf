resource "aws_elasticache_replication_group" "redis" {
  replication_group_id       = "${var.environment}-redis"
  description                = "Redis cluster for Scorpius Platform"
  node_type                  = var.node_type
  num_cache_clusters         = var.num_cache_clusters
  port                       = 6379
  engine                     = "redis"
  engine_version             = "7.0"
  automatic_failover_enabled = true
  multi_az_enabled           = true
  vpc_security_group_ids     = [aws_security_group.redis.id]
  subnet_group_name          = aws_elasticache_subnet_group.redis.name
  parameter_group_name       = aws_elasticache_parameter_group.redis.name
  maintenance_window         = "sun:04:00-sun:05:00"
  security_group_ids         = [aws_security_group.redis.id]
  tags = {
    Environment = var.environment
    Project     = "scorpius-enterprise"
  }
}

resource "aws_elasticache_subnet_group" "redis" {
  name        = "${var.environment}-redis-subnet-group"
  description = "Redis subnet group for Scorpius"
  subnet_ids  = var.private_subnet_ids
}

resource "aws_elasticache_parameter_group" "redis" {
  name        = "${var.environment}-redis-params"
  family      = "redis7.0"
  description = "Redis parameter group for Scorpius"

  parameter {
    name  = "maxmemory-policy"
    value = "allkeys-lru"
  }

  parameter {
    name  = "maxmemory"
    value = "-1"
  }
}

resource "aws_security_group" "redis" {
  name_prefix = "${var.environment}-redis"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = var.ingress_cidr_blocks
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

output "endpoint" {
  description = "Redis cluster endpoint"
  value       = aws_elasticache_replication_group.redis.primary_endpoint_address
  sensitive   = true
}

output "port" {
  description = "Redis port"
  value       = aws_elasticache_replication_group.redis.port
}
