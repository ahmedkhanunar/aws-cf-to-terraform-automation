output "lambda_names" {
  value = keys(aws_lambda_function.managed)
}
