resource "aws_dynamodb_table" "managed" {
  for_each = var.dynamodb_tables

  name         = each.value.table_name
  billing_mode = try(each.value.billing_mode, "PAY_PER_REQUEST")

  # Only required if using PROVISIONED billing_mode
  read_capacity  = each.value.billing_mode == "PROVISIONED" ? try(each.value.read_capacity, 1) : null
  write_capacity = each.value.billing_mode == "PROVISIONED" ? try(each.value.write_capacity, 1) : null

  # Extract hash_key and range_key from key_schema list
  hash_key = lookup({ for k in each.value.key_schema : k.KeyType => k.AttributeName }, "HASH", null)
  range_key = lookup({ for k in each.value.key_schema : k.KeyType => k.AttributeName }, "RANGE", null)

  dynamic "attribute" {
    for_each = each.value.attributes
    content {
      name = attribute.value.AttributeName
      type = attribute.value.AttributeType
    }
  }

  point_in_time_recovery {
    enabled = try(each.value.pitr_enabled, false)
  }

  tags = merge(
    try(each.value.tags, {}),
    {
      ManagedBy = "terraform"
      Imported  = "true"
    }
  )

  lifecycle {
    ignore_changes = [
      deletion_protection_enabled,
      billing_mode,
      point_in_time_recovery,
      global_secondary_index,
      attribute,
      replica,
      stream_enabled,
      stream_view_type
    ]
  }
}