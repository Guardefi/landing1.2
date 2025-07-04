resource "aws_db_instance" "postgresql" {
  identifier              = "${var.environment}-postgresql"
  engine                  = "postgres"
  engine_version          = "15.4"
  instance_class          = var.instance_class
  allocated_storage       = var.allocated_storage
  max_allocated_storage   = var.max_allocated_storage
  storage_type           = "gp3"
  storage_encrypted       = true
  kms_key_id             = aws_kms_key.rds.id
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.rds.name
  skip_final_snapshot    = true
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  monitoring_interval    = 60
  monitoring_role_arn    = aws_iam_role.rds_monitoring.arn
  performance_insights_enabled = true
  performance_insights_retention_period = 7
  enable_performance_insights = true
  performance_insights_kms_key_id = aws_kms_key.rds.id
  enable_cloudwatch_logs_exports = ["postgresql"]
  parameter_group_name    = aws_db_parameter_group.postgresql.name
  tags = {
    Environment = var.environment
    Project     = "scorpius-enterprise"
  }
}

resource "aws_db_parameter_group" "postgresql" {
  name        = "${var.environment}-postgresql-params"
  family      = "postgres15"
  description = "PostgreSQL parameter group for Scorpius"

  parameter {
    name  = "log_min_duration_statement"
    value = "100"
  }

  parameter {
    name  = "log_statement"
    value = "error"
  }

  parameter {
    name  = "shared_buffers"
    value = "25%"
  }
}

resource "aws_db_subnet_group" "rds" {
  name        = "${var.environment}-rds-subnet-group"
  subnet_ids  = var.private_subnet_ids
  description = "RDS subnet group for Scorpius"
}

resource "aws_security_group" "rds" {
  name_prefix = "${var.environment}-rds"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 5432
    to_port     = 5432
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

resource "aws_kms_key" "rds" {
  description = "KMS key for RDS encryption"
  deletion_window_in_days = 7

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "*"
        }
        Action = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow use of the key"
        Effect = "Allow"
        Principal = {
          AWS = ["${data.aws_caller_identity.current.arn}"]
        }
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role" "rds_monitoring" {
  name = "${var.environment}-rds-monitoring-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "rds_monitoring" {
  role       = aws_iam_role.rds_monitoring.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

output "endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.postgresql.endpoint
  sensitive   = true
}

output "password" {
  description = "RDS instance password"
  value       = aws_db_instance.postgresql.password
  sensitive   = true
}
