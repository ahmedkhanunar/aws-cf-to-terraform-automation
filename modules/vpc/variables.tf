variable "vpcs" {
  type = map(object({
    cidr_block           = string
    instance_tenancy     = optional(string)
    enable_dns_support   = optional(bool)
    enable_dns_hostnames = optional(bool)
    tags                 = optional(list(object({ Key = string, Value = string })))
  }))
}

variable "tags" {
  type    = map(string)
  default = {}
}

variable "environment" {
  type = string
}
