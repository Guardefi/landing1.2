variable "project" {
  description = "Project name prefix"
  type        = string
}

variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "db_engine_version" {
  type    = string
  default = "15.4"
}

variable "db_instance_class" {
  type    = string
  default = "db.t3.medium"
}

variable "db_name" {
  type    = string
  default = "scorpius"
}

variable "db_username" {
  type    = string
  default = "scorpius"
}

variable "db_password" {
  type      = string
  sensitive = true
}

variable "redis_engine_version" {
  type    = string
  default = "7.1"
}

variable "redis_node_type" {
  type    = string
  default = "cache.t3.micro"
}

variable "k8s_version" {
  type    = string
  default = "1.29"
}

variable "worker_instance_type" {
  type    = string
  default = "t3.medium"
}

variable "domain_name" {
  description = "Root domain for ACM / ALB"
  type        = string
} 