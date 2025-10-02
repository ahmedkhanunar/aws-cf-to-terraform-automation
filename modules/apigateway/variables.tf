variable "apis" {
  type = map(object({
    name          = string
    description   = string
    endpoint_type = string
    resources = map(object({
      path_part  = string
      parent_id  = string
      methods    = map(object({
        http_method  = string
        integration  = object({
          type                = string
          uri                 = string
          http_method         = string
          credentials         = string
          request_templates   = map(string)
        })
      }))
    }))
    stage_name  = string
  }))
}

variable "environment" {
  type        = string
  description = "Environment name"
}

variable "tags" {
  type        = map(string)
  description = "Common tags for all resources"
  default     = {}
}