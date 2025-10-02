resource "aws_nat_gateway" "managed" {
  for_each = var.nat_gateways

  allocation_id = each.value.elastic_ip
  subnet_id     = each.value.subnet_id

  tags = merge(
    var.tags,
    {
      managed_by  = "terraform"
      environment = var.environment
    },
    { for tag in coalesce(each.value.tags, []) : tag.Key => tag.Value }
  )

  lifecycle {
    ignore_changes = [tags_all, allocation_id,tags]
  }
}
