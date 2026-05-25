resource "aws_s3_bucket" "main" {
  bucket = "${var.project_name}-${var.environment}-${data.aws_caller_identity.current.account_id}"

  tags = {
    Name        = var.project_name
    Environment = var.environment
  }
}

resource "aws_s3_bucket_versioning" "main" {
  bucket = aws_s3_bucket.main.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "main" {
  bucket = aws_s3_bucket.main.id

  rule {
    id     = "expire_old_jobs"
    status = "Enabled"

    filter {
      prefix = "jobs/"
    }

    expiration {
      days = 7 # Clean up after 7 days
    }
  }

  rule {
    id     = "expire_old_outputs"
    status = "Enabled"

    filter {
      prefix = "outputs/"
    }

    expiration {
      days = 30
    }
  }
}

data "aws_caller_identity" "current" {}
