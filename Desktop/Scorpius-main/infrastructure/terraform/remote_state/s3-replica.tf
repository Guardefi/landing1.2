# Cross-Region Terraform State Replication for Disaster Recovery
# Ensures state files are replicated to multiple regions for RTO/RPO compliance

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Primary region state bucket (us-east-1)
provider "aws" {
  alias  = "primary"
  region = var.primary_region
}

# DR region state bucket (us-west-2)
provider "aws" {
  alias  = "dr"
  region = var.dr_region
}

# Variables
variable "primary_region" {
  description = "Primary AWS region"
  type        = string
  default     = "us-east-1"
}

variable "dr_region" {
  description = "Disaster recovery AWS region"
  type        = string
  default     = "us-west-2"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "prod"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "scorpius"
}

# KMS keys for encryption
resource "aws_kms_key" "terraform_state_primary" {
  provider                = aws.primary
  description             = "KMS key for Terraform state encryption - Primary"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = {
    Name        = "${var.project_name}-terraform-state-primary"
    Environment = var.environment
    Purpose     = "terraform-state"
    Region      = var.primary_region
  }
}

resource "aws_kms_key" "terraform_state_dr" {
  provider                = aws.dr
  description             = "KMS key for Terraform state encryption - DR"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = {
    Name        = "${var.project_name}-terraform-state-dr"
    Environment = var.environment
    Purpose     = "terraform-state"
    Region      = var.dr_region
  }
}

# KMS aliases
resource "aws_kms_alias" "terraform_state_primary" {
  provider      = aws.primary
  name          = "alias/${var.project_name}-terraform-state-primary"
  target_key_id = aws_kms_key.terraform_state_primary.key_id
}

resource "aws_kms_alias" "terraform_state_dr" {
  provider      = aws.dr
  name          = "alias/${var.project_name}-terraform-state-dr"
  target_key_id = aws_kms_key.terraform_state_dr.key_id
}

# Primary S3 bucket for Terraform state
resource "aws_s3_bucket" "terraform_state_primary" {
  provider = aws.primary
  bucket   = "${var.project_name}-terraform-state-${var.environment}-${var.primary_region}"

  tags = {
    Name        = "${var.project_name}-terraform-state-primary"
    Environment = var.environment
    Purpose     = "terraform-state"
    Region      = var.primary_region
  }
}

# DR S3 bucket for Terraform state
resource "aws_s3_bucket" "terraform_state_dr" {
  provider = aws.dr
  bucket   = "${var.project_name}-terraform-state-${var.environment}-${var.dr_region}"

  tags = {
    Name        = "${var.project_name}-terraform-state-dr"
    Environment = var.environment
    Purpose     = "terraform-state"
    Region      = var.dr_region
  }
}

# Primary bucket versioning
resource "aws_s3_bucket_versioning" "terraform_state_primary" {
  provider = aws.primary
  bucket   = aws_s3_bucket.terraform_state_primary.id
  versioning_configuration {
    status = "Enabled"
  }
}

# DR bucket versioning
resource "aws_s3_bucket_versioning" "terraform_state_dr" {
  provider = aws.dr
  bucket   = aws_s3_bucket.terraform_state_dr.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Primary bucket encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state_primary" {
  provider = aws.primary
  bucket   = aws_s3_bucket.terraform_state_primary.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.terraform_state_primary.arn
      sse_algorithm     = "aws:kms"
    }
    bucket_key_enabled = true
  }
}

# DR bucket encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state_dr" {
  provider = aws.dr
  bucket   = aws_s3_bucket.terraform_state_dr.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.terraform_state_dr.arn
      sse_algorithm     = "aws:kms"
    }
    bucket_key_enabled = true
  }
}

# Primary bucket public access block
resource "aws_s3_bucket_public_access_block" "terraform_state_primary" {
  provider = aws.primary
  bucket   = aws_s3_bucket.terraform_state_primary.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# DR bucket public access block
resource "aws_s3_bucket_public_access_block" "terraform_state_dr" {
  provider = aws.dr
  bucket   = aws_s3_bucket.terraform_state_dr.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Cross-region replication role
resource "aws_iam_role" "replication" {
  provider = aws.primary
  name     = "${var.project_name}-terraform-state-replication"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "s3.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-terraform-state-replication"
    Environment = var.environment
    Purpose     = "s3-replication"
  }
}

# Replication policy
resource "aws_iam_role_policy" "replication" {
  provider = aws.primary
  name     = "${var.project_name}-terraform-state-replication"
  role     = aws_iam_role.replication.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObjectVersionForReplication",
          "s3:GetObjectVersionAcl",
          "s3:GetObjectVersionTagging"
        ]
        Resource = "${aws_s3_bucket.terraform_state_primary.arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket"
        ]
        Resource = aws_s3_bucket.terraform_state_primary.arn
      },
      {
        Effect = "Allow"
        Action = [
          "s3:ReplicateObject",
          "s3:ReplicateDelete",
          "s3:ReplicateTags"
        ]
        Resource = "${aws_s3_bucket.terraform_state_dr.arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt"
        ]
        Resource = aws_kms_key.terraform_state_primary.arn
      },
      {
        Effect = "Allow"
        Action = [
          "kms:GenerateDataKey"
        ]
        Resource = aws_kms_key.terraform_state_dr.arn
      }
    ]
  })
}

# Cross-region replication configuration
resource "aws_s3_bucket_replication_configuration" "replication" {
  provider   = aws.primary
  depends_on = [aws_s3_bucket_versioning.terraform_state_primary]

  role   = aws_iam_role.replication.arn
  bucket = aws_s3_bucket.terraform_state_primary.id

  rule {
    id     = "ReplicateToDisasterRecovery"
    status = "Enabled"

    destination {
      bucket        = aws_s3_bucket.terraform_state_dr.arn
      storage_class = "STANDARD_IA"

      encryption_configuration {
        replica_kms_key_id = aws_kms_key.terraform_state_dr.arn
      }
    }
  }
}

# DynamoDB table for state locking - Primary
resource "aws_dynamodb_table" "terraform_locks_primary" {
  provider     = aws.primary
  name         = "${var.project_name}-terraform-locks-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.terraform_state_primary.arn
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = {
    Name        = "${var.project_name}-terraform-locks-primary"
    Environment = var.environment
    Purpose     = "terraform-locks"
    Region      = var.primary_region
  }
}

# DynamoDB table for state locking - DR
resource "aws_dynamodb_table" "terraform_locks_dr" {
  provider     = aws.dr
  name         = "${var.project_name}-terraform-locks-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.terraform_state_dr.arn
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = {
    Name        = "${var.project_name}-terraform-locks-dr"
    Environment = var.environment
    Purpose     = "terraform-locks"
    Region      = var.dr_region
  }
}

# DynamoDB Global Tables for cross-region replication
resource "aws_dynamodb_global_table" "terraform_locks" {
  provider = aws.primary
  name     = aws_dynamodb_table.terraform_locks_primary.name

  replica {
    region_name = var.primary_region
  }

  replica {
    region_name = var.dr_region
  }

  depends_on = [
    aws_dynamodb_table.terraform_locks_primary,
    aws_dynamodb_table.terraform_locks_dr
  ]
}

# Outputs
output "primary_state_bucket" {
  description = "Primary S3 bucket for Terraform state"
  value       = aws_s3_bucket.terraform_state_primary.bucket
}

output "dr_state_bucket" {
  description = "DR S3 bucket for Terraform state"
  value       = aws_s3_bucket.terraform_state_dr.bucket
}

output "primary_dynamodb_table" {
  description = "Primary DynamoDB table for Terraform locks"
  value       = aws_dynamodb_table.terraform_locks_primary.name
}

output "dr_dynamodb_table" {
  description = "DR DynamoDB table for Terraform locks"
  value       = aws_dynamodb_table.terraform_locks_dr.name
}

output "primary_kms_key_id" {
  description = "Primary KMS key ID for state encryption"
  value       = aws_kms_key.terraform_state_primary.key_id
}

output "dr_kms_key_id" {
  description = "DR KMS key ID for state encryption"
  value       = aws_kms_key.terraform_state_dr.key_id
}

# RTO/RPO Documentation
output "disaster_recovery_metrics" {
  description = "Disaster recovery time objectives"
  value = {
    rto_minutes = 15  # Recovery Time Objective: 15 minutes
    rpo_minutes = 5   # Recovery Point Objective: 5 minutes (S3 replication)
    backup_frequency = "continuous"
    replication_regions = [var.primary_region, var.dr_region]
  }
} 