output "state_machine_arns" {
  value       = { for k, v in aws_sfn_state_machine.managed : k => v.arn }
  description = "Map of Step Functions state machine ARNs"
}

output "state_machine_names" {
  value       = { for k, v in aws_sfn_state_machine.managed : k => v.name }
  description = "Map of Step Functions state machine names"
}


