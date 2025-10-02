variable "environment" {
  type        = string
  description = "Environment name"
}

variable "tags" {
  type        = map(string)
  description = "Common tags for all resources"
  default     = {}
}

variable "eips" {
  description = "Map of Elastic IPs and their configurations."
  type = map(object({
    allocation_id  = string
    public_ip      = string
    association_id = optional(string)
    tags           = optional(list(object({
      Key   = string
      Value = string
    })), [])
  }))
}
