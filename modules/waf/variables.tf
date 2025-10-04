variable "environment" {
  type        = string
  description = "Environment name"
}

variable "tags" {
  type        = map(string)
  description = "Common tags for all resources"
  default     = {}
}

variable "web_acls" {
  description = "List of Web ACLs to manage"
  type = map(object({
    name        = string
    id          = string
    arn         = string
    scope       = string
    description = string
    visibility_config = object({
      SampledRequestsEnabled = bool
      CloudWatchMetricsEnabled = bool
      MetricName = string
    })
    tags = map(string)
    ip_sets = list(string)
  }))
}

variable "ip_sets" {
  description = "Map of IP Sets configurations"
  type = map(object({
    name               = string
    description        = string
    scope              = string
    ip_address_version = string
    addresses          = list(string)
    tags               = map(string)
  }))
}

