output "lambda_layer_arns" {
  value = { for k, v in aws_lambda_layer_version.managed : k => v.arn }
  description = "Map of Lambda layer ARNs"
}

output "lambda_layer_versions" {
  value = { for k, v in aws_lambda_layer_version.managed : k => v.version }
  description = "Map of Lambda layer versions"
}

output "lambda_layer_layer_arns" {
  value = { for k, v in aws_lambda_layer_version.managed : k => v.layer_arn }
  description = "Map of Lambda layer ARNs (without version)"
}

output "lambda_layer_names" {
  value = { for k, v in aws_lambda_layer_version.managed : k => v.layer_name }
  description = "Map of Lambda layer names"
}
