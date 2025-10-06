variable "environment" {
  type        = string
  description = "Environment name"
}

variable "tags" {
  type        = map(string)
  description = "Common tags for all resources"
  default     = {}
}

variable "state_machines" {
  description = "Map of Step Functions state machine configurations"
  type = map(object({
    name                   = string
    definition             = string
    role_arn               = string
    type                   = optional(string)
    logging_configuration  = optional(object({
      include_execution_data = optional(bool)
      level                  = optional(string)
      log_destination        = optional(string)
    }))
    tracing_configuration  = optional(object({
      enabled = optional(bool)
    }))
    tags = optional(map(string))
  }))
  default = {}
}


