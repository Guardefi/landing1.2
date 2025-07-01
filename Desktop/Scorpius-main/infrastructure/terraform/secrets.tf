# AWS Secrets Manager Configuration for Scorpius Enterprise Platform
# This configuration creates secrets with automatic rotation

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Variables
variable "environment" {
  description = "Environment name (staging/production)"
  type        = string
  validation {
    condition     = contains(["staging", "production"], var.environment)
    error_message = "Environment must be either 'staging' or 'production'."
  }
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "scorpius"
}

# Local values
locals {
  secret_prefix = "${var.app_name}/${var.environment}"
  
  common_tags = {
    Environment = var.environment
    Application = var.app_name
    ManagedBy   = "Terraform"
  }
}

# === DATABASE SECRETS ===
resource "aws_secretsmanager_secret" "database" {
  name        = "${local.secret_prefix}/database"
  description = "Database credentials for ${var.app_name} ${var.environment}"
  
  tags = merge(local.common_tags, {
    SecretType = "database"
  })
}

resource "aws_secretsmanager_secret_version" "database" {
  secret_id = aws_secretsmanager_secret.database.id
  secret_string = jsonencode({
    username = "scorpius_app"
    password = random_password.db_password.result
    host     = aws_db_instance.main.endpoint
    port     = aws_db_instance.main.port
    database = aws_db_instance.main.db_name
    url      = "postgresql://${aws_db_instance.main.username}:${random_password.db_password.result}@${aws_db_instance.main.endpoint}:${aws_db_instance.main.port}/${aws_db_instance.main.db_name}"
  })
}

# Database password rotation
resource "aws_secretsmanager_secret_rotation" "database" {
  secret_id           = aws_secretsmanager_secret.database.id
  rotation_lambda_arn = aws_lambda_function.rotation.arn
  
  rotation_rules {
    automatically_after_days = 90
  }
}

# === REDIS SECRETS ===
resource "aws_secretsmanager_secret" "redis" {
  name        = "${local.secret_prefix}/redis"
  description = "Redis credentials for ${var.app_name} ${var.environment}"
  
  tags = merge(local.common_tags, {
    SecretType = "redis"
  })
}

resource "aws_secretsmanager_secret_version" "redis" {
  secret_id = aws_secretsmanager_secret.redis.id
  secret_string = jsonencode({
    host     = aws_elasticache_replication_group.main.primary_endpoint_address
    port     = aws_elasticache_replication_group.main.port
    password = random_password.redis_password.result
    url      = "redis://:${random_password.redis_password.result}@${aws_elasticache_replication_group.main.primary_endpoint_address}:${aws_elasticache_replication_group.main.port}/0"
  })
}

# === JWT SECRETS ===
resource "aws_secretsmanager_secret" "jwt_secret" {
  name        = "${local.secret_prefix}/jwt-secret"
  description = "JWT signing secret for ${var.app_name} ${var.environment}"
  
  tags = merge(local.common_tags, {
    SecretType = "jwt"
  })
}

resource "aws_secretsmanager_secret_version" "jwt_secret" {
  secret_id = aws_secretsmanager_secret.jwt_secret.id
  secret_string = jsonencode({
    secret_key = random_password.jwt_secret.result
    algorithm  = "HS256"
    expires_in = 3600
  })
}

# JWT secret rotation
resource "aws_secretsmanager_secret_rotation" "jwt_secret" {
  secret_id           = aws_secretsmanager_secret.jwt_secret.id
  rotation_lambda_arn = aws_lambda_function.jwt_rotation.arn
  
  rotation_rules {
    automatically_after_days = 90
  }
}

# === WEB3 PROVIDER SECRETS ===
resource "aws_secretsmanager_secret" "web3_providers" {
  name        = "${local.secret_prefix}/web3-providers"
  description = "Web3 provider API keys for ${var.app_name} ${var.environment}"
  
  tags = merge(local.common_tags, {
    SecretType = "web3"
  })
}

resource "aws_secretsmanager_secret_version" "web3_providers" {
  secret_id = aws_secretsmanager_secret.web3_providers.id
  secret_string = jsonencode({
    infura_url      = "https://mainnet.infura.io/v3/${var.infura_project_id}"
    alchemy_url     = "https://eth-mainnet.alchemyapi.io/v2/${var.alchemy_api_key}"
    quicknode_url   = "https://distinguished-clean-lake.quiknode.pro/${var.quicknode_api_key}/"
    etherscan_key   = var.etherscan_api_key
  })
}

# === ROTATION LAMBDA FUNCTION ===
resource "aws_lambda_function" "rotation" {
  filename         = "rotation_lambda.zip"
  function_name    = "${var.app_name}-${var.environment}-secret-rotation"
  role            = aws_iam_role.rotation_lambda.arn
  handler         = "index.handler"
  runtime         = "python3.11"
  timeout         = 300
  
  environment {
    variables = {
      ENVIRONMENT = var.environment
      LOG_LEVEL   = "INFO"
    }
  }
  
  tags = local.common_tags
}

# JWT rotation lambda (separate from DB rotation)
resource "aws_lambda_function" "jwt_rotation" {
  filename         = "jwt_rotation_lambda.zip"
  function_name    = "${var.app_name}-${var.environment}-jwt-rotation"
  role            = aws_iam_role.rotation_lambda.arn
  handler         = "jwt_rotation.handler"
  runtime         = "python3.11"
  timeout         = 60
  
  environment {
    variables = {
      ENVIRONMENT = var.environment
      LOG_LEVEL   = "INFO"
    }
  }
  
  tags = local.common_tags
}

# === IAM ROLES AND POLICIES ===
resource "aws_iam_role" "rotation_lambda" {
  name = "${var.app_name}-${var.environment}-rotation-lambda"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
  
  tags = local.common_tags
}

resource "aws_iam_role_policy" "rotation_lambda" {
  name = "${var.app_name}-${var.environment}-rotation-lambda-policy"
  role = aws_iam_role.rotation_lambda.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:PutSecretValue",
          "secretsmanager:UpdateSecretVersionStage"
        ]
        Resource = [
          aws_secretsmanager_secret.database.arn,
          aws_secretsmanager_secret.jwt_secret.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "rds:DescribeDBInstances",
          "rds:ModifyDBInstance"
        ]
        Resource = "*"
      }
    ]
  })
}

# === RANDOM PASSWORDS ===
resource "random_password" "db_password" {
  length  = 32
  special = true
}

resource "random_password" "redis_password" {
  length  = 32
  special = false  # Redis doesn't support all special characters
}

resource "random_password" "jwt_secret" {
  length  = 64
  special = true
}

# === OUTPUTS ===
output "database_secret_arn" {
  description = "ARN of the database secret"
  value       = aws_secretsmanager_secret.database.arn
}

output "redis_secret_arn" {
  description = "ARN of the Redis secret"
  value       = aws_secretsmanager_secret.redis.arn
}

output "jwt_secret_arn" {
  description = "ARN of the JWT secret"
  value       = aws_secretsmanager_secret.jwt_secret.arn
}

output "web3_secret_arn" {
  description = "ARN of the Web3 providers secret"
  value       = aws_secretsmanager_secret.web3_providers.arn
}
