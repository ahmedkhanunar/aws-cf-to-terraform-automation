variable "distributions" {
  description = "Map of CloudFront distributions to create"
  type = map(object({
    enabled             = bool
    is_ipv6_enabled     = optional(bool, false)
    comment             = optional(string)
    default_root_object = optional(string)
    price_class         = optional(string)
    http_version        = optional(string)
    web_acl_id          = optional(string)

    origins = list(object({
      domain_name      = string
      origin_id        = string
      origin_path      = optional(string)
      custom_headers   = optional(list(object({
        name  = string
        value = string
      })), [])
      s3_origin_config = optional(object({
        origin_access_identity = optional(string)
      }))
      custom_origin_config = optional(object({
        http_port                = optional(number, 80)
        https_port               = optional(number, 443)
        origin_protocol_policy   = optional(string, "http-only")
        origin_ssl_protocols     = optional(list(string), ["TLSv1.2"])
        origin_keepalive_timeout = optional(number)
        origin_read_timeout      = optional(number)
      }))
    }))

    default_cache_behavior = object({
      allowed_methods  = optional(list(string), ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"])
      cached_methods   = optional(list(string), ["GET", "HEAD"])
      target_origin_id = string
      compress         = optional(bool, false)
      viewer_protocol_policy = optional(string, "allow-all")
      min_ttl          = optional(number, 0)
      default_ttl      = optional(number, 86400)
      max_ttl          = optional(number, 31536000)
      forwarded_values = object({
        query_string = optional(bool, false)
        headers      = optional(list(string), [])
        cookies = object({
          forward = optional(string, "none")
        })
      })
      lambda_function_associations = optional(list(object({
        event_type   = string
        lambda_arn   = string
        include_body = optional(bool, false)
      })), [])
      function_associations = optional(list(object({
        event_type   = string
        function_arn = string
      })), [])
    })

    cache_behaviors = optional(list(object({
      path_pattern         = string
      allowed_methods      = optional(list(string), ["GET", "HEAD"])
      cached_methods       = optional(list(string), ["GET", "HEAD"])
      target_origin_id     = string
      compress             = optional(bool, false)
      viewer_protocol_policy = optional(string, "allow-all")
      min_ttl              = optional(number, 0)
      default_ttl          = optional(number, 86400)
      max_ttl              = optional(number, 31536000)
      forwarded_values = object({
        query_string = optional(bool, false)
        headers      = optional(list(string), [])
        cookies = object({
          forward = optional(string, "none")
        })
      })
      lambda_function_associations = optional(list(object({
        event_type   = string
        lambda_arn   = string
        include_body = optional(bool, false)
      })), [])
      function_associations = optional(list(object({
        event_type   = string
        function_arn = string
      })), [])
    })), [])

    restrictions = optional(object({
      geo_restriction = optional(object({
        restriction_type = optional(string, "none")
        locations        = optional(list(string), [])
      }))
    }))

    viewer_certificate = optional(object({
      cloudfront_default_certificate = optional(bool, false)
      iam_certificate_id             = optional(string)
      acm_certificate_arn            = optional(string)
      ssl_support_method             = optional(string)
      minimum_protocol_version       = optional(string)
    }))

    custom_error_responses = optional(list(object({
      error_code          = number
      response_code       = optional(number)
      response_page_path  = optional(string)
      error_caching_min_ttl = optional(number)
    })), [])

    aliases = optional(list(string), [])

    logging = optional(object({
      bucket          = string
      include_cookies = optional(bool, false)
      prefix          = optional(string)
    }))

    tags = optional(map(string), {})
  }))
  default = {}
}

variable "tags" {
  description = "Common tags to apply to CloudFront distributions"
  type        = map(string)
  default     = {}
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = ""
}

