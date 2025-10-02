variable "environment" {
  type    = string
  default = "qa"
}

variable "tags" {
  description = "Tags for resources"
  type        = map(string)
  default     = {}
}

variable "dynamodb_tables" {
  description = "Map of DynamoDB tables with full configuration"
  type = map(object({
    table_name    = string
    region        = optional(string)    # region usually handled by provider config
    status        = optional(string)    # not used in resource, metadata only
    billing_mode  = string
    read_capacity  = optional(number)
    write_capacity = optional(number)
    key_schema    = list(object({
      AttributeName = string
      KeyType       = string
    }))
    attributes = list(object({
      AttributeName = string
      AttributeType = string
    }))
    pitr_enabled  = optional(bool, false)
    tags          = optional(map(string), {})
  }))
  default = {}
}
