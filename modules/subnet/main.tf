resource "aws_subnet" "managed" {
  for_each = var.subnets

  vpc_id                  = each.value.vpc_id
  cidr_block              = each.value.cidr_block
  availability_zone_id    = each.value.availability_zone_id
  map_public_ip_on_launch = try(each.value.map_public_ip_on_launch, false)

  tags = merge(
    var.tags,
    { ManagedBy = "terraform", Imported = "true", Environment = var.environment }
  )

  lifecycle {
    ignore_changes = [tags_all, tags]
  }
}
