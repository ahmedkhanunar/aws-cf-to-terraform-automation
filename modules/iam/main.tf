# IAM Roles
resource "aws_iam_role" "managed" {
  for_each = var.roles

  name                 = each.value.role_name
  path                 = try(each.value.path, "/")
  assume_role_policy   = each.value.assume_role_policy  # Already JSON string
  description          = try(each.value.description, null)
  max_session_duration = try(each.value.max_session_duration, 3600)
  permissions_boundary = try(each.value.permissions_boundary, null)

  tags = merge(
    var.tags,
    try(each.value.tags, {}),
    { ManagedBy = "terraform", Imported = "true" }
  )

  lifecycle {
    ignore_changes = [
      description,
      permissions_boundary,
      tags,
    ]
  }
}

# --- Managed Policy Attachments ---
locals {
  role_policy_attachments = flatten([
    for role_name, role in var.roles : [
      for policy_arn in try(role.attached_managed_policies, []) : {
        role_name  = role_name
        policy_arn = policy_arn
      }
    ]
  ])
}

resource "aws_iam_role_policy_attachment" "managed" {
  for_each = {
    for rp in local.role_policy_attachments :
    # "${rp.role_name}-${replace(rp.policy_arn, "[:/]", "_")}" => rp
    "${rp.role_name}-${replace(replace(rp.policy_arn, ":", "_"), "/", "_")}" => rp
  }

  role       = aws_iam_role.managed[each.value.role_name].name
  policy_arn = each.value.policy_arn
}

# --- Inline Policies ---
resource "aws_iam_role_policy" "inline" {
  for_each = var.inline_policies

  name   = each.value.policy_name
  role   = aws_iam_role.managed[each.value.role_id].id
  policy = each.value.policy_json  # Already a JSON string

  depends_on = [aws_iam_role.managed]
}
