variable "topics" {
  type = map(object({
    name                        = string
    display_name                = optional(string)
    fifo_topic                  = optional(bool)
    content_based_deduplication = optional(bool)
    # tags                        = optional(list(object({ Key = string, Value = string })))
    subscriptions               = optional(list(object({
      protocol = string
      endpoint = string
      subscription_arn = optional(string)  # <-- Add this line
    })))
  }))
}

variable "environment" {
  type        = string
  description = "Environment name"
}

variable "tags" {
  type        = map(string)
  description = "Common tags for all resources"
  default     = {}
}
