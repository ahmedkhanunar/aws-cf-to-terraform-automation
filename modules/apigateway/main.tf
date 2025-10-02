# Create REST APIs using the same pattern
resource "aws_api_gateway_rest_api" "managed" {
  for_each = var.apis

  name        = each.value.name
  description = each.value.description
  endpoint_configuration {
    types = [try(each.value.endpoint_type, "REGIONAL")] # Default to 'REGIONAL'
  }

  tags = merge(
    var.tags,
    { ManagedBy = "terraform", Imported = "true", Environment = var.environment }
  )

  lifecycle {
    ignore_changes = [
      endpoint_configuration,
      tags_all
    ]
  }
}

# Handle resources in the API (path parts)
# resource "aws_api_gateway_resource" "managed" {
#   for_each = {
#     for api_id, api_data in var.apis : api_id => api_data.resources
#   }

#   rest_api_id = aws_api_gateway_rest_api.managed[each.key].id
#   parent_id   = each.value.parent_id
#   path_part   = each.value.path_part
# }

# Handle methods for each resource
# resource "aws_api_gateway_method" "managed" {
#   for_each = {
#     for resource_id, resource_data in var.apis : resource_id => resource_data.resources
#   }

#   rest_api_id   = aws_api_gateway_rest_api.managed[each.key].id
#   resource_id   = aws_api_gateway_resource.managed[each.key].id
#   http_method   = each.value.methods[0].http_method
#   authorization = try(each.value.methods[0].authorization, "NONE") # Default to 'NONE' if null

#   lifecycle {
#     ignore_changes = [
#       authorization
#     ]
#   }
# }

# Handle integration for each method
# resource "aws_api_gateway_integration" "managed" {
#   for_each = {
#     for resource_id, resource_data in var.apis : resource_id => resource_data.resources
#   }

#   rest_api_id           = aws_api_gateway_rest_api.managed[each.key].id
#   resource_id           = aws_api_gateway_resource.managed[each.key].id
#   http_method           = aws_api_gateway_method.managed[each.key].http_method
#   integration_http_method = each.value.methods[0].integration.http_method
#   type                  = each.value.methods[0].integration.type
#   uri                   = each.value.methods[0].integration.uri
#   credentials           = each.value.methods[0].integration.credentials
#   request_templates     = each.value.methods[0].integration.request_templates
# }

# # Create API Gateway stages (deployment environments)
# resource "aws_api_gateway_stage" "managed" {
#   for_each = var.apis

#   rest_api_id  = aws_api_gateway_rest_api.managed[each.key].id
#   stage_name   = each.value.stage_name
#   deployment_id = aws_api_gateway_deployment.managed[each.key].id
# }

# Handle deployment for each REST API
# resource "aws_api_gateway_deployment" "managed" {
#   for_each = var.apis

#   rest_api_id = aws_api_gateway_rest_api.managed[each.key].id
#   stage_name  = each.value.stage_name
#   triggers = {
#     redeployment = md5(jsonencode(each.value.resources))
#   }
# }

# Optional: Handle the OPTIONS method if required for CORS
# resource "aws_api_gateway_method" "managed_options" {
#   for_each = {
#     for api_id, api_data in var.apis : api_id => api_data.resources
#     if contains(keys(each.value.methods), "OPTIONS")
#   }

#   rest_api_id   = aws_api_gateway_rest_api.managed[each.key].id
#   resource_id   = aws_api_gateway_resource.managed[each.key].id
#   http_method   = "OPTIONS"
#   authorization = "NONE" # CORS doesn't require authorization

#   lifecycle {
#     ignore_changes = [
#       authorization
#     ]
#   }
# }

# Integration for OPTIONS method (CORS)
# resource "aws_api_gateway_integration" "managed_options_integration" {
#   for_each = {
#     for api_id, api_data in var.apis : api_id => api_data.resources
#     if contains(keys(each.value.methods), "OPTIONS")
#   }

#   rest_api_id           = aws_api_gateway_rest_api.managed[each.key].id
#   resource_id           = aws_api_gateway_resource.managed[each.key].id
#   http_method           = "OPTIONS"
#   integration_http_method = "MOCK" # Use MOCK for CORS
#   type                  = "MOCK"
#   request_templates     = {
#     "application/json" = "{\"statusCode\": 200}"
#   }

#   integration_responses = {
#     "200" = {
#       status_code = "200"
#       response_parameters = {
#         "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key'"
#         "method.response.header.Access-Control-Allow-Methods" = "'GET,POST,OPTIONS'"
#         "method.response.header.Access-Control-Allow-Origin" = "'*'"
#       }
#     }
#   }
# }

# Enable method responses for OPTIONS method (CORS)
# resource "aws_api_gateway_method_response" "managed_options_method_response" {
#   for_each = {
#     for api_id, api_data in var.apis : api_id => api_data.resources
#     if contains(keys(each.value.methods), "OPTIONS")
#   }

#   rest_api_id   = aws_api_gateway_rest_api.managed[each.key].id
#   resource_id   = aws_api_gateway_resource.managed[each.key].id
#   http_method   = "OPTIONS"
#   status_code   = "200"
#   response_parameters = {
#     "method.response.header.Access-Control-Allow-Headers" = true
#     "method.response.header.Access-Control-Allow-Methods" = true
#     "method.response.header.Access-Control-Allow-Origin" = true
#   }
# }

# Enable integration responses for OPTIONS method (CORS)
# resource "aws_api_gateway_integration_response" "managed_options_integration_response" {
#   for_each = {
#     for api_id, api_data in var.apis : api_id => api_data.resources
#     if contains(keys(each.value.methods), "OPTIONS")
#   }

#   rest_api_id           = aws_api_gateway_rest_api.managed[each.key].id
#   resource_id           = aws_api_gateway_resource.managed[each.key].id
#   http_method           = "OPTIONS"
#   status_code           = "200"
#   selection_pattern     = ".*"
#   response_parameters   = {
#     "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key'"
#     "method.response.header.Access-Control-Allow-Methods" = "'GET,POST,OPTIONS'"
#     "method.response.header.Access-Control-Allow-Origin" = "'*'"
#   }
# }
