variable "environment" {
  type        = string
  description = "Environment name"
}

variable "tags" {
  type        = map(string)
  description = "Common tags for all resources"
  default     = {}
}

variable "nat_gateways" {
  description = "Map of NAT Gateway configurations."
  type = map(object({
    nat_gateway_id = string
    subnet_id      = string
    state          = string
    elastic_ip     = string
    tags           = list(object({
      Key   = string
      Value = string
    }))
  }))
  default = {}
}
