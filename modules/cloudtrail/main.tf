resource "aws_cloudtrail" "managed" {
  for_each = var.cloudtrails

  name                          = each.value.name
  s3_bucket_name                = each.value.s3_bucket_name
  s3_key_prefix                 = each.value.s3_key_prefix
  sns_topic_name                = each.value.sns_topic_name

  include_global_service_events = each.value.include_global_service_events
  is_multi_region_trail         = each.value.is_multi_region_trail
  is_organization_trail         = each.value.is_organization_trail
  enable_log_file_validation    = each.value.log_file_validation_enabled

  cloud_watch_logs_group_arn    = each.value.cloud_watch_logs_log_group_arn
  cloud_watch_logs_role_arn     = each.value.cloud_watch_logs_role_arn
  kms_key_id                   = each.value.kms_key_id

  tags = merge(
    var.tags,
    {
      ManagedBy   = "terraform"
      Imported    = "true"
      Environment = var.environment
    },
    { for tag in each.value.tags : tag.Key => tag.Value }
  )

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [
      name,
      s3_bucket_name,
      sns_topic_name,
      kms_key_id,
      cloud_watch_logs_group_arn,
      cloud_watch_logs_role_arn
    ]
  }
}
