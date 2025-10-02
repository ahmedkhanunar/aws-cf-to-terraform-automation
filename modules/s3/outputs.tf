output "s3_bucket_ids" {
  value = { for k, v in aws_s3_bucket.managed : k => v.id }
}

output "s3_bucket_arns" {
  value = { for k, v in aws_s3_bucket.managed : k => v.arn }
}

output "s3_bucket_names" {
  value = keys(aws_s3_bucket.managed)
}
