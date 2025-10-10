resource "aws_sqs_queue" "managed" {
  for_each = var.sqs_queues

  name                      = each.value.name
  delay_seconds             = try(each.value.delay_seconds, 0)
  max_message_size          = try(each.value.max_message_size, 262144)
  message_retention_seconds = try(each.value.message_retention_seconds, 1209600)
  receive_wait_time_seconds = try(each.value.receive_wait_time_seconds, 0)
  visibility_timeout_seconds = try(each.value.visibility_timeout_seconds, 30)
  sqs_managed_sse_enabled   = try(each.value.sqs_managed_sse_enabled, true)
  # kms_master_key_id         = try(each.value.kms_master_key_id, null)
  kms_data_key_reuse_period_seconds = try(each.value.kms_data_key_reuse_period_seconds, 300)

  # Dead letter queue configuration
  # dynamic "redrive_policy" {
  #   for_each = try(each.value.redrive_policy, null) != null ? [each.value.redrive_policy] : []
  #   content {
  #     dead_letter_target_arn = redrive_policy.value.dead_letter_target_arn
  #     max_receive_count      = redrive_policy.value.max_receive_count
  #   }
  # }

  # FIFO queue configuration
  fifo_queue                  = try(each.value.fifo_queue, false)
  content_based_deduplication = try(each.value.content_based_deduplication, false)
  deduplication_scope         = try(each.value.deduplication_scope, null)
  fifo_throughput_limit       = try(each.value.fifo_throughput_limit, null)

  tags = merge(
    var.tags,
    try(each.value.tags, {}),
    { ManagedBy = "terraform", Imported = "true", Environment = var.environment }
  )

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      redrive_policy,
      kms_master_key_id,
      kms_data_key_reuse_period_seconds
    ]
  }
}

resource "aws_sqs_queue_policy" "managed" {
  for_each = {
    for k, v in var.sqs_queues : k => v
    if try(v.policy, null) != null
  }

  queue_url = aws_sqs_queue.managed[each.key].id
  policy    = each.value.policy

  lifecycle {
    prevent_destroy = true
    ignore_changes = [policy]
  }
}

