variable "secrets" {
  type = map(object({
    name                = string
    description         = string
    kms_key_id          = optional(string)
    rotation_enabled    = optional(bool)
    rotation_lambda_arn = optional(string)
    tags                = optional(list(object({ Key = string, Value = string })))
    # value is excluded intentionally
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