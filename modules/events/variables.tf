variable "environment" {
  type        = string
  description = "Environment name"
}

variable "tags" {
  type        = map(string)
  description = "Common tags for all resources"
  default     = {}
}

variable "event_rules" {
  description = "Map of EventBridge rule configurations"
  type = map(object({
    name                = string
    description         = optional(string)
    schedule_expression = optional(string)
    event_pattern       = optional(string)
    role_arn           = optional(string)
    is_enabled         = optional(bool)
    event_bus_name     = optional(string)
    targets            = optional(object({
      target_id = string
      arn       = string
      input     = optional(string)
      input_path = optional(string)
      role_arn  = optional(string)
      ecs_target = optional(object({
        task_definition_arn = string
        launch_type         = string
        network_configuration = object({
          subnets          = list(string)
          security_groups  = list(string)
          assign_public_ip = bool
        })
      }))
    }))
    tags = optional(map(string))
  }))
  default = {}
}
