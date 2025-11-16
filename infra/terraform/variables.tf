variable "project_name" {
  description = "Project name for tagging and resource naming"
  type        = string
  default     = "neuropredict-ai"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "backup_retention_days" {
  description = "Retention in days for S3 backup lifecycle"
  type        = number
  default     = 14
}


