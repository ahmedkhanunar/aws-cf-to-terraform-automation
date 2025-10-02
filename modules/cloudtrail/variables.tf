variable "cloudtrails" {
  type = map(object({
    name                         = string
    s3_bucket_name               = string
    s3_key_prefix                = string
    sns_topic_name               = string
    include_global_service_events = bool
    is_multi_region_trail        = bool
    is_organization_trail        = bool
    log_file_validation_enabled  = bool
    cloud_watch_logs_log_group_arn = string
    cloud_watch_logs_role_arn    = string
    kms_key_id                   = string
    tags                        = list(object({ Key = string, Value = string }))
  }))
}

variable "environment" {
  type = string
}

variable "tags" {
  type    = map(string)
  default = {}
}