resource "aws_eip" "managed" {
  for_each = var.eips

  tags = merge(
    var.tags,
    {
      managed_by  = "terraform"
      environment = var.environment
    },
    { for tag in coalesce(each.value.tags, []) : tag.Key => tag.Value }
  )

  lifecycle {
    ignore_changes = [tags]
  }
}
