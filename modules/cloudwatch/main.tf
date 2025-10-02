resource "aws_cloudwatch_log_group" "managed" {
  for_each = var.log_groups

  name              = each.value.name
  retention_in_days = each.value.retention_in_days

  tags = each.value.tags

  lifecycle {
    ignore_changes = [tags]
  }
}
