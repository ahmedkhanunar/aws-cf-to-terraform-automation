resource "aws_kms_key" "managed" {
  for_each = var.kms_keys

  description             = each.value.description
  key_usage              = try(each.value.key_usage, "ENCRYPT_DECRYPT")
  customer_master_key_spec = try(each.value.customer_master_key_spec, "SYMMETRIC_DEFAULT")
  enable_key_rotation    = try(each.value.key_rotation_enabled, false)
  deletion_window_in_days = try(each.value.deletion_window_in_days, 10)
  
  policy = try(each.value.policy, null)

  tags = merge(
    var.tags,
    try(each.value.tags, {}),
    { ManagedBy = "terraform", Imported = "true", Environment = var.environment }
  )

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      deletion_window_in_days,
      policy,
      bypass_policy_lockout_safety_check
    ]
  }
}
resource "aws_kms_alias" "managed" {
  for_each = var.kms_aliases

  name          = each.key
  target_key_id = each.value

  lifecycle {
    prevent_destroy = true
  }
}