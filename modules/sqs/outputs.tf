output "sqs_queue_urls" {
  value = { for k, v in aws_sqs_queue.managed : k => v.url }
  description = "Map of SQS queue URLs"
}

output "sqs_queue_arns" {
  value = { for k, v in aws_sqs_queue.managed : k => v.arn }
  description = "Map of SQS queue ARNs"
}

output "sqs_queue_names" {
  value = { for k, v in aws_sqs_queue.managed : k => v.name }
  description = "Map of SQS queue names"
}

output "sqs_queue_policy_ids" {
  value = { for k, v in aws_sqs_queue_policy.managed : k => v.id }
  description = "Map of SQS queue policy IDs"
}
