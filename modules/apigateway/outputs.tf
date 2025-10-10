output "rest_api_ids" {
  description = "Rest API IDs keyed by input rid"
  value       = { for k, v in aws_api_gateway_rest_api.managed : k => v.id }
}

output "domain_name_arns" {
  description = "Domain name ARNs keyed by domain name"
  value       = { for k, v in aws_api_gateway_domain_name.managed : k => v.arn }
}

output "stage_arns" {
  description = "Stage ARNs keyed by input rid"
  value       = { for k, v in aws_api_gateway_stage.managed : k => v.arn }
}


