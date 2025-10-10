resource "aws_sfn_state_machine" "managed" {
  for_each = var.state_machines

  name       = each.value.name
  role_arn   = each.value.role_arn
  definition = each.value.definition
  type       = try(each.value.type, null)

  dynamic "logging_configuration" {
    for_each = try(each.value.logging_configuration, null) != null ? [each.value.logging_configuration] : []
    content {
      include_execution_data = try(logging_configuration.value.include_execution_data, null)
      level                  = try(logging_configuration.value.level, null)
      log_destination        = try(logging_configuration.value.log_destination, null)
    }
  }

  dynamic "tracing_configuration" {
    for_each = try(each.value.tracing_configuration, null) != null ? [each.value.tracing_configuration] : []
    content {
      enabled = try(tracing_configuration.value.enabled, null)
    }
  }

  tags = merge(
    var.tags,
    try(each.value.tags, {}),
    { ManagedBy = "terraform", Imported = "true", Environment = var.environment }
  )

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      definition,
      tags
    ]
  }
}


