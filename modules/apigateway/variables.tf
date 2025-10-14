variable "environment" {
  type = string
}

variable "tags" {
  type    = map(string)
  default = {}
}

variable "rest_apis" {
  description = "Map keyed by CFN rid to RestApi configs"
  type = map(object({
    id                        = string
    name                      = string
    description               = optional(string)
    api_key_source            = optional(string)
    endpoint_configuration    = optional(object({
      types = optional(list(string))
      ipAddressType = optional(string)
    }))
    binary_media_types        = optional(list(string))
    minimum_compression_size  = optional(number)
    policy                    = optional(string)
    tags                      = optional(map(string))
    version                   = optional(string)
    warnings                  = optional(list(string))
  }))
  default = {}
}

variable "account" {
  description = "Map keyed by CFN rid to API Gateway account config"
  type = map(object({
    cloudwatchRoleArn = optional(string)
    throttleSettings = optional(object({
      burstLimit = optional(number)
      rateLimit  = optional(number)
    }))
    features = optional(list(string))
    account_id = optional(string)
  }))
  default = {}
}

variable "domain_names" {
  description = "Map keyed by domain name (rid) to domain configs"
  type = map(object({
    domain_name                   = string
    certificate_arn               = optional(string)
    certificate_name              = optional(string)
    certificate_upload_date       = optional(string)
    distribution_domain_name      = optional(string)
    distribution_hosted_zone_id   = optional(string)
    regional_domain_name          = optional(string)
    regional_hosted_zone_id       = optional(string)
    regional_certificate_arn      = optional(string)
    regional_certificate_name     = optional(string)
    endpoint_configuration        = optional(object({
      types = optional(list(string))
    }))
    mutual_tls_authentication     = optional(object({
      truststore_uri     = optional(string)
      truststore_version = optional(string)
    }))
    security_policy              = optional(string)
    tags                         = optional(map(string))
  }))
  default = {}
}

variable "stages" {
  description = "Map keyed by CFN rid to stage configs including rest_api_id and stage_name"
  type = map(object({
    rest_api_id           = string
    stage_name           = string
    deployment_id        = optional(string)
    description          = optional(string)
    cache_cluster_enabled = optional(bool)
    cache_cluster_size   = optional(string)
    variables            = optional(map(string))
    documentation_version = optional(string)
    tracing_enabled      = optional(bool)
    access_log_settings  = optional(object({
      destinationArn = optional(string)
      format         = optional(string)
    }))
    canary_settings      = optional(object({
      percent_traffic = optional(number)
      deployment_id   = optional(string)
      stage_variable_overrides = optional(map(string))
      use_stage_cache = optional(bool)
    }))
    tags                 = optional(map(string))
    web_acl_arn          = optional(string)
    method_settings      = optional(list(object({
      resource_path = optional(string)
      http_method   = optional(string)
      throttling_burst_limit = optional(number)
      throttling_rate_limit  = optional(number)
      caching_enabled         = optional(bool)
      cache_ttl_in_seconds   = optional(number)
      cache_data_encrypted   = optional(bool)
      require_authorization_for_cache_control = optional(bool)
      unauthorized_cache_control_header_strategy = optional(string)
    })), [])
  }))
  default = {}
}

variable "resources" {
  description = "Map keyed by resource id to API Gateway resource configs"
  type        = any
  default     = {}
}

variable "methods" {
  description = "Map keyed by resourceId|httpMethod to API Gateway method configs"
  type        = any
  default     = {}
}

variable "method_responses" {
  description = "Map keyed by resourceId|httpMethod|statusCode to method response configs"
  type        = any
  default     = {}
}

variable "integrations" {
  description = "Map keyed by resourceId|httpMethod to integration configs"
  type        = any
  default     = {}
}

variable "integration_responses" {
  description = "Map keyed by resourceId|httpMethod|statusCode to integration response configs"
  type        = any
  default     = {}
}

variable "deployments" {
  description = "Map keyed by deployment id to deployment configs"
  type        = any
  default     = {}
}

variable "base_path_mappings" {
  description = "Map keyed by domain|basePath to base path mapping configs"
  type        = any
  default     = {}
}


