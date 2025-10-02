resource "aws_vpc" "managed" {
  for_each = var.vpcs

  cidr_block           = each.value.cidr_block
  instance_tenancy     = try(each.value.instance_tenancy, "default")
  enable_dns_support   = try(each.value.enable_dns_support, true)
  enable_dns_hostnames = try(each.value.enable_dns_hostnames, true)

  tags = merge(
    var.tags,
    tomap({ for tag in try(each.value.tags, []) : tag.Key => tag.Value }),
    {
      ManagedBy   = "terraform",
      Imported    = "true",
      Environment = var.environment
    }
  )

  lifecycle {
    ignore_changes = [
      tags["aws:cloudformation:logical-id"],
      tags["aws:cloudformation:stack-id"],
      tags["aws:cloudformation:stack-name"],
      tags["lambda:createdBy"],
      tags_all,
      tags
      ]
  }
}
