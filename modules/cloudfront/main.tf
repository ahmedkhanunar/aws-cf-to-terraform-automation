resource "aws_cloudfront_distribution" "managed" {
  for_each = var.distributions

  enabled             = each.value.enabled
  is_ipv6_enabled     = try(each.value.is_ipv6_enabled, false)
  comment             = try(each.value.comment, null)
  default_root_object = try(each.value.default_root_object, null)
  price_class         = try(each.value.price_class, null)
  http_version        = try(each.value.http_version, null)
  web_acl_id          = try(each.value.web_acl_id, null)

  # Origins
  dynamic "origin" {
    for_each = each.value.origins
    content {
      domain_name = origin.value.domain_name
      origin_id   = origin.value.origin_id
      origin_path = try(origin.value.origin_path, null)

      dynamic "s3_origin_config" {
        for_each = try(origin.value.s3_origin_config != null, false) ? [origin.value.s3_origin_config] : []
        content {
          origin_access_identity = try(s3_origin_config.value.origin_access_identity, null)
        }
      }

      dynamic "custom_origin_config" {
        for_each = try(origin.value.custom_origin_config != null, false) ? [origin.value.custom_origin_config] : []
        content {
          http_port                = try(custom_origin_config.value.http_port, 80)
          https_port               = try(custom_origin_config.value.https_port, 443)
          origin_protocol_policy   = try(custom_origin_config.value.origin_protocol_policy, "http-only")
          origin_ssl_protocols     = try(custom_origin_config.value.origin_ssl_protocols, ["TLSv1.2"])
          origin_keepalive_timeout = try(custom_origin_config.value.origin_keepalive_timeout, null)
          origin_read_timeout      = try(custom_origin_config.value.origin_read_timeout, null)
        }
      }

      dynamic "custom_header" {
        for_each = try(origin.value.custom_headers != null ? origin.value.custom_headers : [], [])
        content {
          name  = custom_header.value.name
          value = custom_header.value.value
        }
      }
    }
  }

  # Default Cache Behavior
  default_cache_behavior {
    allowed_methods  = try(each.value.default_cache_behavior.allowed_methods, ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"])
    cached_methods   = try(each.value.default_cache_behavior.cached_methods, ["GET", "HEAD"])
    target_origin_id = each.value.default_cache_behavior.target_origin_id
    compress         = try(each.value.default_cache_behavior.compress, false)

    viewer_protocol_policy = try(each.value.default_cache_behavior.viewer_protocol_policy, "allow-all")
    min_ttl                = try(each.value.default_cache_behavior.min_ttl, 0)
    default_ttl            = try(each.value.default_cache_behavior.default_ttl, 86400)
    max_ttl                = try(each.value.default_cache_behavior.max_ttl, 31536000)

    forwarded_values {
      query_string = try(each.value.default_cache_behavior.forwarded_values.query_string, false)
      headers      = try(each.value.default_cache_behavior.forwarded_values.headers, [])
      cookies {
        forward = try(each.value.default_cache_behavior.forwarded_values.cookies.forward, "none")
      }
    }

    dynamic "lambda_function_association" {
      for_each = try(each.value.default_cache_behavior.lambda_function_associations != null ? each.value.default_cache_behavior.lambda_function_associations : [], [])
      content {
        event_type   = lambda_function_association.value.event_type
        lambda_arn   = lambda_function_association.value.lambda_arn
        include_body = try(lambda_function_association.value.include_body, false)
      }
    }

    dynamic "function_association" {
      for_each = try(each.value.default_cache_behavior.function_associations != null ? each.value.default_cache_behavior.function_associations : [], [])
      content {
        event_type   = function_association.value.event_type
        function_arn = function_association.value.function_arn
      }
    }
  }

  # Cache Behaviors
  dynamic "ordered_cache_behavior" {
    for_each = try(each.value.cache_behaviors != null ? each.value.cache_behaviors : [], [])
    content {
      path_pattern     = ordered_cache_behavior.value.path_pattern
      allowed_methods  = try(ordered_cache_behavior.value.allowed_methods, ["GET", "HEAD"])
      cached_methods   = try(ordered_cache_behavior.value.cached_methods, ["GET", "HEAD"])
      target_origin_id = ordered_cache_behavior.value.target_origin_id
      compress         = try(ordered_cache_behavior.value.compress, false)

      viewer_protocol_policy = try(ordered_cache_behavior.value.viewer_protocol_policy, "allow-all")
      min_ttl                = try(ordered_cache_behavior.value.min_ttl, 0)
      default_ttl            = try(ordered_cache_behavior.value.default_ttl, 86400)
      max_ttl                = try(ordered_cache_behavior.value.max_ttl, 31536000)

      forwarded_values {
        query_string = try(ordered_cache_behavior.value.forwarded_values.query_string, false)
        headers      = try(ordered_cache_behavior.value.forwarded_values.headers, [])
        cookies {
          forward = try(ordered_cache_behavior.value.forwarded_values.cookies.forward, "none")
        }
      }

      dynamic "lambda_function_association" {
        for_each = try(ordered_cache_behavior.value.lambda_function_associations != null ? ordered_cache_behavior.value.lambda_function_associations : [], [])
        content {
          event_type   = lambda_function_association.value.event_type
          lambda_arn   = lambda_function_association.value.lambda_arn
          include_body = try(lambda_function_association.value.include_body, false)
        }
      }

      dynamic "function_association" {
        for_each = try(ordered_cache_behavior.value.function_associations != null ? ordered_cache_behavior.value.function_associations : [], [])
        content {
          event_type   = function_association.value.event_type
          function_arn = function_association.value.function_arn
        }
      }
    }
  }

  # Restrictions
  dynamic "restrictions" {
    for_each = try(each.value.restrictions != null ? [each.value.restrictions] : [], [])
    content {
      dynamic "geo_restriction" {
        for_each = try(restrictions.value.geo_restriction != null ? [restrictions.value.geo_restriction] : [], [])
        content {
          restriction_type = try(geo_restriction.value.restriction_type, "none")
          locations        = try(geo_restriction.value.locations, [])
        }
      }
    }
  }

  # Viewer Certificate
  dynamic "viewer_certificate" {
    for_each = try(each.value.viewer_certificate != null ? [each.value.viewer_certificate] : [], [])
    content {
      cloudfront_default_certificate = try(viewer_certificate.value.cloudfront_default_certificate, false)
      iam_certificate_id             = try(viewer_certificate.value.iam_certificate_id, null)
      acm_certificate_arn            = try(viewer_certificate.value.acm_certificate_arn, null)
      ssl_support_method             = try(viewer_certificate.value.ssl_support_method, null)
      minimum_protocol_version       = try(viewer_certificate.value.minimum_protocol_version, null)
    }
  }

  # Custom Error Responses
  dynamic "custom_error_response" {
    for_each = try(each.value.custom_error_responses != null ? each.value.custom_error_responses : [], [])
    content {
      error_code         = custom_error_response.value.error_code
      response_code      = try(custom_error_response.value.response_code, null)
      response_page_path = try(custom_error_response.value.response_page_path, null)
      error_caching_min_ttl = try(custom_error_response.value.error_caching_min_ttl, null)
    }
  }

  # Aliases
  aliases = try(each.value.aliases, [])

  # Logging
  dynamic "logging_config" {
    for_each = try(each.value.logging != null ? [each.value.logging] : [], [])
    content {
      bucket          = logging_config.value.bucket
      include_cookies = try(logging_config.value.include_cookies, false)
      prefix          = try(logging_config.value.prefix, null)
    }
  }

  tags = merge(
    var.tags,
    try(each.value.tags, {}),
    {
      ManagedBy = "terraform"
      Imported  = "true"
    }
  )

  lifecycle {
    ignore_changes = [tags]
  }

  # CloudFront distributions take time to deploy
  wait_for_deployment = false
}

