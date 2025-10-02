# -------------------------------------
# AWS Config Configuration Recorders
# -------------------------------------
resource "aws_config_configuration_recorder" "managed" {
  for_each = var.recorders

  name     = each.value.config.name
  role_arn = each.value.config.roleARN

  recording_group {
    all_supported                  = try(each.value.config.recordingGroup.allSupported, true)
    include_global_resource_types = try(each.value.config.recordingGroup.includeGlobalResourceTypes, false)
    resource_types                = try(each.value.config.recordingGroup.resourceTypes, [])

    dynamic "exclusion_by_resource_types" {
      for_each = (
        try(each.value.config.recordingGroup.allSupported, true) == false &&
        length(try(each.value.config.recordingGroup.exclusionByResourceTypes.resourceTypes, [])) > 0
      ) ? [1] : []

      content {
        resource_types = each.value.config.recordingGroup.exclusionByResourceTypes.resourceTypes
      }
    }

    dynamic "recording_strategy" {
      for_each = try(each.value.config.recordingGroup.recordingStrategy, null) != null ? [1] : []
      content {
        use_only = each.value.config.recordingGroup.recordingStrategy.useOnly
      }
    }
  }

  dynamic "recording_mode" {
    for_each = try(each.value.config.recordingMode, null) != null ? [1] : []
    content {
      recording_frequency = try(each.value.config.recordingMode.recordingFrequency, "CONTINUOUS")
      # recording_mode_overrides = try(each.value.config.recordingMode.recordingModeOverrides, [])
    }
  }

  lifecycle {
    ignore_changes = []
  }
}

# -------------------------------------
# AWS Config Delivery Channels
# -------------------------------------
resource "aws_config_delivery_channel" "managed" {
  for_each = var.delivery_channels

  name           = each.value.config.name
  s3_bucket_name = each.value.config.s3BucketName
  s3_key_prefix  = try(each.value.config.s3KeyPrefix, null)
  sns_topic_arn  = try(each.value.config.snsTopicARN, null)

  dynamic "snapshot_delivery_properties" {
    for_each = each.value.config.configSnapshotDeliveryProperties != null ? [each.value.config.configSnapshotDeliveryProperties] : []
    content {
      delivery_frequency = snapshot_delivery_properties.value.deliveryFrequency
    }
  }

  depends_on = [
    aws_config_configuration_recorder.managed
  ]

  lifecycle {
    ignore_changes = []
  }
}

# -------------------------------------
# AWS Config Recorder Status
# -------------------------------------
resource "aws_config_configuration_recorder_status" "managed" {
  for_each = var.recorders

  name       = each.value.config.name
  is_enabled = try(each.value.status.recording, true)

  depends_on = [
    aws_config_configuration_recorder.managed,
    aws_config_delivery_channel.managed
  ]
}
