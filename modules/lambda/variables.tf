variable "functions" {
  description = "Map of Lambda function configurations"
  type = map(object({
    handler               = string
    runtime               = string
    role                  = string
    memory_size           = number
    timeout               = number
    dummy_filename        = optional(string)
    description           = optional(string)
    tracing_mode          = optional(string)
    dead_letter_queue     = optional(string)
    kms_key_arn           = optional(string)
    package_type          = optional(string, "Zip")
    image_config = optional(object({
      command            = optional(list(string))
      entry_point        = optional(list(string))
      working_directory  = optional(string)
    }), {})
    environment_variables = optional(map(string))
    layers                = optional(list(string), [])
    architectures         = optional(list(string), ["x86_64"])
    ephemeral_storage     = optional(number)
    tags                  = optional(map(string), {})
    subnet_ids            = optional(list(string), [])
    security_group_ids    = optional(list(string), [])

    # 👇 Versioning and alias support
    publish_version       = optional(bool, false)
    version_description   = optional(string)
    alias_name            = optional(string)
    alias_description     = optional(string)
  }))
  default = {}
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
