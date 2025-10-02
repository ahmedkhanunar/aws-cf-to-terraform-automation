variable "roles" {
  type = map(object({
    role_name                 = string
    path                      = optional(string, "/")
    assume_role_policy        = any
    description               = optional(string, "")
    max_session_duration      = optional(number, 3600)
    permissions_boundary      = optional(string, null)
    tags                      = optional(map(string), {})
    attached_managed_policies = optional(list(string), [])
    inline_policies = optional(map(object({
      Version = string
      Statement = any
    })), {})

  }))
}

variable "tags" {
  description = "Common tags to apply to IAM roles"
  type        = map(string)
  default     = {}
}
