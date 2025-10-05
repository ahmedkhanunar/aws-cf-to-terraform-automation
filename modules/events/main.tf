resource "aws_cloudwatch_event_rule" "managed" {
  for_each = var.event_rules

  name                = each.value.name
  description         = try(each.value.description, "")
  schedule_expression = try(each.value.schedule_expression, null)
  event_pattern       = try(each.value.event_pattern, null)
  role_arn           = try(each.value.role_arn, null)
#   is_enabled         = try(each.value.is_enabled, true)
  event_bus_name     = try(each.value.event_bus_name, "default")

  tags = merge(
    var.tags,
    try(each.value.tags, {}),
    { ManagedBy = "terraform", Imported = "true", Environment = var.environment }
  )

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      event_pattern,
      schedule_expression
    ]
  }
}

resource "aws_cloudwatch_event_target" "managed" {
  for_each = {
    for k, v in var.event_rules : k => v
    if try(v.targets, null) != null
  }

  rule      = aws_cloudwatch_event_rule.managed[each.key].name
  target_id = each.value.targets.target_id
  arn       = each.value.targets.arn

  # Optional target parameters
  input     = try(each.value.targets.input, null)
  input_path = try(each.value.targets.input_path, null)
  role_arn  = try(each.value.targets.role_arn, null)

  # ECS target specific
  dynamic "ecs_target" {
    for_each = try(each.value.targets.ecs_target, null) != null ? [each.value.targets.ecs_target] : []
    content {
      task_definition_arn = ecs_target.value.task_definition_arn
      launch_type         = ecs_target.value.launch_type
      network_configuration {
        subnets          = ecs_target.value.network_configuration.subnets
        security_groups  = ecs_target.value.network_configuration.security_groups
        assign_public_ip = ecs_target.value.network_configuration.assign_public_ip
      }
    }
  }

  # Lambda targets don't need special configuration blocks
  # The input parameter above handles Lambda input

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      input,
      input_path,
      role_arn,
      input_transformer
    ]
  }
}
