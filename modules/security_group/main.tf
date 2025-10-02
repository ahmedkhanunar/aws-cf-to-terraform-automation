resource "aws_security_group" "managed" {
  for_each = var.security_groups

  vpc_id      = each.value.vpc_id
  name        = each.value.group_name
  description = each.value.description

  tags = merge(
    var.tags,
    {
      managed_by  = "terraform"
      environment = var.environment
    },
    # Only include tags if they are defined (i.e., not an empty list)
    # { for tag in coalesce(each.value.tags, []) : tag.key => tag.value }
  )

  lifecycle {
    ignore_changes = [tags_all, revoke_rules_on_delete, tags]
  }
}

resource "aws_security_group_rule" "ingress" {
  for_each = merge(
    [
      for sg_key, sg in var.security_groups :
      {
        for rule in coalesce(sg.ip_permissions, []) :
        # Key for each rule is a combination of sg_key and rule details to make it unique
        "${sg_key}-${rule.from_port}-${rule.to_port}-${rule.ip_protocol}" => {
          security_group_id = aws_security_group.managed[sg_key].id
          type              = "ingress"
          from_port         = rule.from_port
          to_port           = rule.to_port
          protocol          = rule.ip_protocol
          cidr_blocks       = [for ip in rule.ip_ranges : ip.cidr_ip]
          ipv6_cidr_blocks  = [for ip in rule.ipv6_ranges : ip.cidr_ipv6]
          prefix_list_ids   = rule.prefix_list_ids
        }
      }
    ]...
  )

  security_group_id = each.value.security_group_id
  type              = each.value.type
  from_port         = each.value.from_port
  to_port           = each.value.to_port
  protocol          = each.value.protocol
  cidr_blocks       = each.value.cidr_blocks
  ipv6_cidr_blocks  = each.value.ipv6_cidr_blocks
  prefix_list_ids   = each.value.prefix_list_ids
}

resource "aws_security_group_rule" "egress" {
  for_each = merge(
    [
      for sg_key, sg in var.security_groups :
      {
        for rule in coalesce(sg.ip_permissions_egress, []) :
        # Key for each rule is a combination of sg_key and rule details to make it unique
        "${sg_key}-${rule.from_port}-${rule.to_port}-${rule.ip_protocol}" => {
          security_group_id = aws_security_group.managed[sg_key].id
          type              = "egress"
          from_port         = rule.from_port
          to_port           = rule.to_port
          protocol          = rule.ip_protocol
          cidr_blocks       = [for ip in rule.ip_ranges : ip.cidr_ip]
          ipv6_cidr_blocks  = [for ip in rule.ipv6_ranges : ip.cidr_ipv6]
          prefix_list_ids   = rule.prefix_list_ids
        }
      }
    ]...
  )

  security_group_id = each.value.security_group_id
  type              = each.value.type
  from_port         = each.value.from_port
  to_port           = each.value.to_port
  protocol          = each.value.protocol
  cidr_blocks       = each.value.cidr_blocks
  ipv6_cidr_blocks  = each.value.ipv6_cidr_blocks
  prefix_list_ids   = each.value.prefix_list_ids
}
