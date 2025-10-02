output "network_acl_ids" {
  description = "Map of created network ACLs"
  value = {
    for k, acl in aws_network_acl.managed : k => acl.id
  }
}

output "network_acl_rule_ids" {
  description = "Map of created Network ACL rule resources"
  value = {
    for k, rule in aws_network_acl_rule.rules : k => rule.id
  }
}

