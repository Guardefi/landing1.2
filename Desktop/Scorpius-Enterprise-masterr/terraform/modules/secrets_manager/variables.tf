variable "environment" {
  description = "The environment for the deployment (e.g., staging, production)"
  type        = string
}

variable "initial_secrets" {
  description = "Initial secrets to store in the secret manager"
  type        = map(string)
  default     = {}
}
