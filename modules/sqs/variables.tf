variable "environment" {
  type        = string
  description = "Environment name"
}

variable "tags" {
  type        = map(string)
  description = "Common tags for all resources"
  default     = {}
}

variable "sqs_queues" {
  description = "Map of SQS queue configurations"
  type = map(object({
    name                              = string
    delay_seconds                     = optional(number)
    max_message_size                  = optional(number)
    message_retention_seconds         = optional(number)
    receive_wait_time_seconds         = optional(number)
    visibility_timeout_seconds        = optional(number)
    sqs_managed_sse_enabled          = optional(bool)
    kms_master_key_id                = optional(string)
    kms_data_key_reuse_period_seconds = optional(number)
    fifo_queue                       = optional(bool)
    content_based_deduplication      = optional(bool)
    deduplication_scope              = optional(string)
    fifo_throughput_limit            = optional(string)
    redrive_policy                   = optional(object({
      dead_letter_target_arn = string
      max_receive_count      = number
    }))
    policy                           = optional(string)
    tags                             = optional(map(string))
  }))
  default = {}
}
