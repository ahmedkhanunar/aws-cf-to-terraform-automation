output "kms_key_ids" {
  value = { for k, v in aws_kms_key.managed : k => v.key_id }
  description = "Map of KMS key IDs"
}

output "kms_key_arns" {
  value = { for k, v in aws_kms_key.managed : k => v.arn }
  description = "Map of KMS key ARNs"
}

output "kms_alias_names" {
  value = { for k, v in aws_kms_alias.managed : k => v.name }
  description = "Map of KMS alias names"
}

output "kms_alias_arns" {
  value = { for k, v in aws_kms_alias.managed : k => v.arn }
  description = "Map of KMS alias ARNs"
}
