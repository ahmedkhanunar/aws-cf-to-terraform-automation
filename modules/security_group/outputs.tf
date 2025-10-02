output "security_group_ids" {
  value = { for k, v in aws_security_group.managed : k => v.id }
}
