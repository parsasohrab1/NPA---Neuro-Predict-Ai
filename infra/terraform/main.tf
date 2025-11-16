terraform {
  required_version = ">= 1.5.0"
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

# S3 bucket for backups (DEV/TEST/STAGE/PROD by workspace)
resource "aws_s3_bucket" "backups" {
  bucket = "${var.project_name}-${terraform.workspace}-backups"
  force_destroy = false
  tags = {
    Project     = var.project_name
    Environment = terraform.workspace
    Purpose     = "database-backups"
  }
}

resource "aws_s3_bucket_versioning" "backups_versioning" {
  bucket = aws_s3_bucket.backups.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "backups_lifecycle" {
  bucket = aws_s3_bucket.backups.id

  rule {
    id     = "retention"
    status = "Enabled"

    expiration {
      days = var.backup_retention_days
    }
  }
}

output "backups_bucket_name" {
  value = aws_s3_bucket.backups.bucket
}


