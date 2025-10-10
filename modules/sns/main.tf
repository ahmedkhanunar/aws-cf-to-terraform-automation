resource "aws_sns_topic" "managed" {
  for_each = var.topics

  name                        = each.value.name
  display_name                = try(each.value.display_name, null)
  fifo_topic                  = try(each.value.fifo_topic, false)
  content_based_deduplication = try(each.value.content_based_deduplication, false)

  tags = merge(
    var.tags,
    { ManagedBy = "terraform", Imported = "true", Environment = var.environment }
  )

  lifecycle {
    ignore_changes = [
      kms_master_key_id,
      tags["aws:cloudformation:logical-id"],
      tags["aws:cloudformation:stack-id"],
      tags["aws:cloudformation:stack-name"],
      tags["lambda:createdBy"],
      tags_all,
      tags
    ]
  }
}

resource "aws_sns_topic_subscription" "managed" {
  for_each = {
    for sub in flatten([
      for topic_arn, topic in var.topics :
      [
        for idx, subscription in try(topic.subscriptions, []) : {
          key        = "${topic_arn}--${idx}"
          topic_arn  = topic_arn
          protocol   = subscription.protocol
          endpoint   = subscription.endpoint
          subscription_arn = subscription.subscription_arn
        }
      ]
    ]) : sub.key => {
      topic_arn = sub.topic_arn
      protocol  = sub.protocol
      endpoint  = sub.endpoint
      subscription_arn = sub.subscription_arn
    }
  }

  topic_arn = each.value.topic_arn
  protocol  = each.value.protocol
  endpoint  = each.value.endpoint

  lifecycle {
    ignore_changes = [
      endpoint_auto_confirms,
      confirmation_timeout_in_minutes
    ]
  }

}

