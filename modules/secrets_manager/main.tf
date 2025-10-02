resource "aws_secretsmanager_secret" "managed" {
  for_each = var.secrets

  name        = each.value.name
  description = each.value.description
  kms_key_id  = try(each.value.kms_key_id, null)

  # ✅ Explicitly set these to suppress diffs
  recovery_window_in_days         = 30
  force_overwrite_replica_secret = false

  tags = merge(
    var.tags,
    { ManagedBy = "terraform", Imported = "true", Environment = var.environment }
  )

  lifecycle {
    ignore_changes = [
      recovery_window_in_days,
      force_overwrite_replica_secret
    ]
  }
}


resource "aws_secretsmanager_secret_rotation" "rotation" {
  for_each = {
    for k, v in var.secrets :
    k => v if try(v.rotation_enabled, false) && try(v.rotation_lambda_arn, null) != null
  }

  secret_id           = aws_secretsmanager_secret.managed[each.key].id
  rotation_lambda_arn = each.value.rotation_lambda_arn

  rotation_rules {
    automatically_after_days = 30
  }
}
