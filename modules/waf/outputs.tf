output "waf_web_acl_arns" {
  value       = { for k, v in aws_wafv2_web_acl.managed : k => v.arn }
  description = "Map of WAFv2 Web ACL ARNs"
}

