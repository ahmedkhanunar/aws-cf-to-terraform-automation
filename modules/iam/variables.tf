variable "roles" {
  description = "Map keyed by role identifier to IAM role configs"
  type = map(object({
    role_name                 = string
    path                      = optional(string, "/")
    assume_role_policy        = string  # JSON string
    description               = optional(string, "")
    max_session_duration      = optional(number, 3600)
    permissions_boundary      = optional(string, null)
    tags                      = optional(map(string), {})
    attached_managed_policies = optional(list(string), [])
  }))
  default = {}
}

variable "inline_policies" {
  description = "Map keyed by role_id|policy_name to inline policy configs"
  type = map(object({
    role_id     = string  # Must match a key from var.roles
    policy_name = string
    policy_json = string  # JSON string
  }))
  default = {}
}

variable "tags" {
  description = "Common tags to apply to IAM roles"
  type        = map(string)
  default     = {}
}
