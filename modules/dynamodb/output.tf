output "dynamodb_table_names" {
  description = "List of DynamoDB tables managed by this module"
  value       = keys(var.dynamodb_tables)
}
