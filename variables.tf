variable "aws_region" {
  description = "AWS Region"
  type        = string
  default     = "sa-east-1" # Brazil region
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "rastreamento-codigos"
}

variable "environment" {
  description = "Environment"
  type        = string
  default     = "production"
}

variable "lambda_timeout" {
  default = 900 # 15 minutes
}

variable "lambda_memory" {
  default = 4096 # MB - good for pandas
}

variable "ephemeral_storage" {
  default = 5120 # 5GB /tmp
}

variable "frontend_bucket_name" {
  description = "Frontend S3 bucket name override"
  type        = string
  default     = null
}
