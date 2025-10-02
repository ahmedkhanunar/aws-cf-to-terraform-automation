resource "aws_internet_gateway" "managed" {
  for_each = var.internet_gateways

  vpc_id = each.value.Attachments[0].VpcId

  tags = merge(
    var.tags,
    { ManagedBy = "terraform", Imported = "true", Environment = var.environment }
  )

  lifecycle {
    ignore_changes = [tags_all,tags]
  }
}

output "igw_ids" {
  value = { for k, v in aws_internet_gateway.managed : k => v.id }
}
