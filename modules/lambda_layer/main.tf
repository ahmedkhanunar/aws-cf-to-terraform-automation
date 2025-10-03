resource "aws_lambda_layer_version" "managed" {
  for_each = var.lambda_layers

  layer_name          = each.value.layer_name
  description         = try(each.value.description, "")
  filename            = try(each.value.filename, null)
  s3_bucket           = try(each.value.s3_bucket, null)
  s3_key              = try(each.value.s3_key, null)
  s3_object_version   = try(each.value.s3_object_version, null)
  compatible_runtimes = try(each.value.compatible_runtimes, [])
  compatible_architectures = try(each.value.compatible_architectures, ["x86_64"])
  license_info        = try(each.value.license_info, null)

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      filename,
      s3_bucket,
      s3_key,
      s3_object_version,
      compatible_architectures,

    ]
  }
}
