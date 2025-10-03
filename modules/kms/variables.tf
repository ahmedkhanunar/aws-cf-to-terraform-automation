variable "environment" {
  type        = string
  description = "Environment name"
}

variable "tags" {
  type        = map(string)
  description = "Common tags for all resources"
  default     = {}
}

variable "kms_keys" {
  description = "Map of KMS key configurations"
  type = map(object({
    description              = string
    key_usage               = optional(string)
    customer_master_key_spec = optional(string)
    key_rotation_enabled    = optional(bool)
    deletion_window_in_days = optional(number)
    policy                  = optional(string)
    alias_name              = optional(string)
    tags                    = optional(map(string))
  }))
  default = {}
}

variable "kms_aliases" {
  description = "KMS aliases and their key mappings"
  type        = map(string)
  default     = {}
}


