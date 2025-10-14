terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
    }
  }
}

locals {
  tags = var.tags
}

resource "aws_api_gateway_rest_api" "managed" {
  for_each = var.rest_apis

  name        = try(each.value.name, each.key)
  description = try(each.value.description, null)
  policy      = try(each.value.policy, null)
  api_key_source = try(each.value.api_key_source, null)

  dynamic "endpoint_configuration" {
    for_each = length(try(each.value.endpoint_configuration.types, [])) > 0 ? [1] : []
    content {
      types = try(each.value.endpoint_configuration.types, null)
    }
  }

  binary_media_types        = try(each.value.binary_media_types, null)
  minimum_compression_size  = try(each.value.minimum_compression_size, null)

  tags = local.tags
}

resource "aws_api_gateway_account" "managed" {
  for_each = var.account
  cloudwatch_role_arn = try(each.value.cloudwatchRoleArn, null)
}

resource "aws_api_gateway_domain_name" "managed" {
  for_each = var.domain_names

  domain_name       = try(each.value.domain_name, each.key)
  security_policy   = try(each.value.security_policy, null)
  certificate_arn   = try(each.value.certificate_arn, null)
  regional_certificate_arn = try(each.value.regional_certificate_arn, null)

  dynamic "endpoint_configuration" {
    for_each = length(try(each.value.endpoint_configuration.types, [])) > 0 ? [1] : []
    content {
      types = try(each.value.endpoint_configuration.types, null)
    }
  }

  tags = local.tags
}

resource "aws_api_gateway_stage" "managed" {
  for_each = var.stages

  rest_api_id   = try(each.value.rest_api_id, null)
  stage_name    = try(each.value.stage_name, each.key)
  deployment_id = try(each.value.deployment_id, null)
  description   = try(each.value.description, null)

  cache_cluster_enabled = try(each.value.cache_cluster_enabled, null)
  cache_cluster_size    = try(each.value.cache_cluster_size, null)
  variables             = try(each.value.variables, null)
  documentation_version = try(each.value.documentation_version, null)
  xray_tracing_enabled  = try(each.value.tracing_enabled, null)

  dynamic "access_log_settings" {
    for_each = try(each.value.access_log_settings, null) != null ? [each.value.access_log_settings] : []
    content {
      destination_arn = try(access_log_settings.value.destinationArn, access_log_settings.value.destination_arn, null)
      format          = try(access_log_settings.value.format, null)
    }
  }

  tags = local.tags
}

resource "aws_api_gateway_resource" "managed" {
  for_each = var.resources

  rest_api_id = each.value.rest_api_id
  parent_id   = each.value.parent_id
  path_part   = each.value.path_part
}

resource "aws_api_gateway_method" "managed" {
  for_each = var.methods

  rest_api_id   = each.value.rest_api_id
  resource_id   = each.value.resource_id
  http_method   = each.value.http_method
  authorization = try(each.value.authorization, "NONE")
  api_key_required = try(each.value.api_key_required, false)

  request_models     = try(each.value.request_models, null)
  request_parameters = try(each.value.request_parameters, null)
}

resource "aws_api_gateway_method_response" "managed" {
  for_each = var.method_responses

  rest_api_id   = each.value.rest_api_id
  resource_id   = each.value.resource_id
  http_method   = each.value.http_method
  status_code   = each.value.status_code

  response_models     = try(each.value.response_models, null)
  response_parameters = try(each.value.response_parameters, null)

  depends_on = [aws_api_gateway_method.managed]
}

resource "aws_api_gateway_integration" "managed" {
  for_each = var.integrations

  rest_api_id = each.value.rest_api_id
  resource_id = each.value.resource_id
  http_method = each.value.http_method

  type                    = try(each.value.type, null)
  integration_http_method = try(each.value.integration_http_method, null)
  uri                     = try(each.value.uri, null)
  credentials             = try(each.value.credentials, null)
  request_parameters      = try(each.value.request_parameters, null)
  request_templates       = try(each.value.request_templates, null)
  passthrough_behavior    = try(each.value.passthrough_behavior, null)
  timeout_milliseconds    = try(each.value.timeout_milliseconds, null)
  cache_namespace         = try(each.value.cache_namespace, null)
  cache_key_parameters    = try(each.value.cache_key_parameters, null)

  depends_on = [aws_api_gateway_method.managed]
}

resource "aws_api_gateway_integration_response" "managed" {
  for_each = var.integration_responses

  rest_api_id = each.value.rest_api_id
  resource_id = each.value.resource_id
  http_method = each.value.http_method
  status_code = each.value.status_code

  response_parameters = try(each.value.response_parameters, null)
  response_templates  = try(each.value.response_templates, null)
  selection_pattern   = try(each.value.selection_pattern, null)

  depends_on = [aws_api_gateway_integration.managed]
}

resource "aws_api_gateway_deployment" "managed" {
  for_each = var.deployments

  rest_api_id = each.value.rest_api_id
  description = try(each.value.description, null)

  # Lifecycle to prevent recreation on every apply
  lifecycle {
    create_before_destroy = true
  }

  depends_on = [
    aws_api_gateway_method.managed,
    aws_api_gateway_integration.managed
  ]
}


