resource "aws_network_acl_rule" "rules" {
  for_each = merge(
    [
      for acl_key, acl in var.network_acls :
      {
        for idx, rule in coalesce(acl.Entries, []) :
        "${acl_key}-${lower(tostring(rule.Egress))}-${rule.RuleNumber}" => {
          acl_key      = acl_key
          rule_number  = rule.RuleNumber
          egress       = rule.Egress
          protocol     = rule.Protocol
          rule_action  = rule.RuleAction
          cidr_block   = rule.CidrBlock
          from_port    = try(rule.PortRange.From, null)
          to_port      = try(rule.PortRange.To, null)
        }
      }
    ]...
  )

  network_acl_id = (
    var.network_acls[each.value.acl_key].IsDefault ?
    aws_default_network_acl.managed[each.value.acl_key].id :
    aws_network_acl.managed[each.value.acl_key].id
  )
  
  rule_number    = each.value.rule_number
  egress         = each.value.egress
  protocol       = each.value.protocol
  rule_action    = each.value.rule_action
  cidr_block     = each.value.cidr_block

  from_port = (
    contains(["6", "17"], each.value.protocol) ? each.value.from_port : null
  )
  to_port = (
    contains(["6", "17"], each.value.protocol) ? each.value.to_port : null
  )
}

resource "aws_network_acl" "managed" {
  for_each = var.network_acls

  vpc_id = each.value.VpcId

  subnet_ids = [
    for assoc in coalesce(each.value.Associations, []) :
    assoc.SubnetId
  ]

  tags = merge(
    var.tags,
    {
      ManagedBy  = "terraform"
      Imported   = "true"
      Environment = var.environment
    },
    { for tag in each.value.Tags : tag.Key => tag.Value }
  )

  lifecycle {
    ignore_changes = [tags_all, tags]
  }
}

resource "aws_default_network_acl" "managed" {
  for_each = {
    for k, v in var.network_acls : k => v if v.IsDefault
  }

  default_network_acl_id = each.key

  subnet_ids = [
    for assoc in coalesce(each.value.Associations, []) :
    assoc.SubnetId
  ]

  tags = merge(
    var.tags,
    {
      ManagedBy  = "terraform"
      Imported   = "true"
      Environment = var.environment
    },
    { for tag in each.value.Tags : tag.Key => tag.Value }
  )

  lifecycle {
    ignore_changes = [tags_all]
  }
}
