resource "aws_lambda_function" "managed" {
  for_each = var.functions

  function_name = each.key
  handler       = each.value.handler
  runtime       = each.value.runtime
  role          = each.value.role
  memory_size   = each.value.memory_size
  timeout       = each.value.timeout
  description = try(each.value.description)


  # 👇 New way to publish versions (replaces aws_lambda_version)
  publish = try(each.value.publish_version, false)

  filename         = each.value.dummy_filename
  source_code_hash = filebase64sha256(each.value.dummy_filename)

  layers        = try(each.value.layers, [])
  architectures = try(each.value.architectures, ["x86_64"])
  kms_key_arn   = try(each.value.kms_key_arn, null)
  package_type  = try(each.value.package_type, "Zip")

  dynamic "image_config" {
    for_each = try(each.value.package_type, "Zip") == "Image" ? [1] : []
    content {
      command           = try(each.value.image_config.command, null)
      entry_point       = try(each.value.image_config.entry_point, null)
      working_directory = try(each.value.image_config.working_directory, null)
    }
  }

  dynamic "environment" {
    for_each = [{}]
    content {
      variables = merge(
        { ENVIRONMENT = var.environment },
        try(each.value.environment_variables, {})
      )
    }
  }

  dynamic "ephemeral_storage" {
    for_each = each.value.ephemeral_storage != null ? [1] : []
    content {
      size = each.value.ephemeral_storage
    }
  }

  dynamic "vpc_config" {
    for_each = length(try(each.value.subnet_ids, [])) > 0 ? [1] : []
    content {
      subnet_ids         = try(each.value.subnet_ids, [])
      security_group_ids = try(each.value.security_group_ids, [])
    }
  }

  # lifecycle {
  #   ignore_changes = [
  #     # filename,
  #     # source_code_hash,
  #     # runtime,
  #     # layers,
  #     description,
  #     # publish,
  #     reserved_concurrent_executions,
  #     environment,
  #     vpc_config
  #     # timeout,
  #     # memory_size
  #   ]
  # }

  lifecycle {
  ignore_changes = [
    description,
    vpc_config,
    environment,
    reserved_concurrent_executions,
  ]
}


  tags = merge(
    var.tags,
    try(each.value.tags, {}),
    { ManagedBy = "terraform", Imported = "true" }
  )
}

# 👇 Alias support (still valid)
resource "aws_lambda_alias" "alias" {
  for_each = {
    for k, v in var.functions : k => v
    if try(v.publish_version, false) && try(v.alias_name, null) != null
  }

  name             = each.value.alias_name
  function_name    = aws_lambda_function.managed[each.key].function_name
  function_version = aws_lambda_function.managed[each.key].version
  description      = try(each.value.alias_description, null)
}
