variable "log_groups" {
  description = "Map of CloudWatch Log Groups to manage"
  type = map(object({
    name              = string
    retention_in_days = optional(number, 90)
    tags              = optional(map(string), {})
  }))
  default = {}
}

variable "environment" {
  type = string
}

variable "tags" {
  type    = map(string)
  default = {}
}