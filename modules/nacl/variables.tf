variable "environment" {
  description = "Environment name (e.g. dev, qa, prod)"
  type        = string
}

variable "tags" {
  description = "Global tags applied to all resources"
  type        = map(string)
  default     = {}
}

variable "network_acls" {
  description = "Map of Network ACLs and their rules/associations"
  type = map(object({
    VpcId     = string
    IsDefault = bool
    Tags      = list(object({
      Key   = string
      Value = string
    }))
    Associations = optional(list(object({
      SubnetId = string
    })), [])
    Entries = optional(list(object({
      CidrBlock   = string
      Egress      = bool
      Protocol    = string
      RuleAction  = string
      RuleNumber  = number
      PortRange   = optional(object({
        From = number
        To   = number
      }))
    })), [])
  }))
}
