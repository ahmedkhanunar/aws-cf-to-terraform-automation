variable "security_groups" {
  description = "Map of security groups with their rules."
  type = map(object({
    vpc_id           = string
    group_name       = string
    description      = string
    ip_permissions   = optional(list(object({
      ip_protocol    = string
      from_port      = optional(number, null)
      to_port        = optional(number, null)
      ip_ranges      = list(object({ cidr_ip = string }))
      ipv6_ranges    = list(object({ cidr_ipv6 = string }))
      prefix_list_ids = list(string)
    })), [])
    ip_permissions_egress = optional(list(object({
      ip_protocol    = string
      from_port      = optional(number, null)
      to_port        = optional(number, null)
      ip_ranges      = list(object({ cidr_ip = string }))
      ipv6_ranges    = list(object({ cidr_ipv6 = string }))
      prefix_list_ids = list(string)
    })), [])
  }))
}


variable "tags" {
  description = "Default tags applied to all resources."
  type        = map(string)
  default     = {}
}

variable "environment" {
  description = "The environment this infrastructure is part of."
  type        = string
  default     = "prod"
}
