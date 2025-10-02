resource "aws_s3_bucket" "managed" {
  for_each = var.buckets

  bucket = each.value.bucket

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [bucket] # keep original bucket name
  }

  tags = merge(
    var.tags,
    { ManagedBy = "terraform", Imported = "true", Environment = var.environment }
  )
}

# Bucket versioning
resource "aws_s3_bucket_versioning" "managed" {
  for_each = var.buckets

  bucket = aws_s3_bucket.managed[each.key].id

  versioning_configuration {
    status = each.value.versioning_status
  }

  lifecycle {
    ignore_changes = [versioning_configuration[0].status]
  }
}

# Bucket encryption (if exists)
resource "aws_s3_bucket_server_side_encryption_configuration" "managed" {
  for_each = var.buckets

  bucket = aws_s3_bucket.managed[each.key].bucket

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
  
  lifecycle {
    ignore_changes = [rule] # Prevent overwriting real AWS encryption config (e.g., aws:kms, bucket_key_enabled)
  }
}
