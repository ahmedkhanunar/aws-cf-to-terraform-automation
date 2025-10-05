output "event_rule_arns" {
  value = { for k, v in aws_cloudwatch_event_rule.managed : k => v.arn }
  description = "Map of EventBridge rule ARNs"
}

output "event_rule_names" {
  value = { for k, v in aws_cloudwatch_event_rule.managed : k => v.name }
  description = "Map of EventBridge rule names"
}

output "event_target_ids" {
  value = { for k, v in aws_cloudwatch_event_target.managed : k => v.target_id }
  description = "Map of EventBridge target IDs"
}
