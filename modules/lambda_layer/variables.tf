variable "environment" {
  type        = string
  description = "Environment name"
}

variable "tags" {
  type        = map(string)
  description = "Common tags for all resources"
  default     = {}
}

variable "lambda_layers" {
  description = "Map of Lambda layer configurations"
  type = map(object({
    layer_name              = string
    description             = optional(string)
    filename                = optional(string)
    s3_bucket               = optional(string)
    s3_key                  = optional(string)
    s3_object_version       = optional(string)
    compatible_runtimes     = optional(list(string))
    compatible_architectures = optional(list(string))
    license_info            = optional(string)
    tags                    = optional(map(string))
  }))
  default = {}
}
