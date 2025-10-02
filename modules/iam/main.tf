# IAM Roles
resource "aws_iam_role" "managed" {
  for_each = var.roles

  name                 = each.value.role_name
  path                 = try(each.value.path, "/")
  assume_role_policy   = jsonencode(each.value.assume_role_policy)
  description          = try(each.value.description, null)
  max_session_duration = try(each.value.max_session_duration, 3600)
  permissions_boundary = try(each.value.permissions_boundary, null)

  tags = merge(
    var.tags,
    each.value.tags, # <--- CORRECTED
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
    "${rp.role_name}-${replace(rp.policy_arn, "[:/]", "_")}" => rp
  }

  role       = aws_iam_role.managed[each.value.role_name].name
  policy_arn = each.value.policy_arn
}

# --- Inline Policies ---
locals {
  role_inline_policies = flatten([
    for role_name, role in var.roles : [
      for policy_name, policy_doc in try(role.inline_policies, {}) : {
        role_name   = role_name
        policy_name = policy_name
        document    = policy_doc
      }
    ]
  ])
}

resource "aws_iam_role_policy" "inline" {
  for_each = {
    for ip in local.role_inline_policies :
    "${ip.role_name}-${ip.policy_name}" => ip
  }

  name   = each.value.policy_name
  role   = aws_iam_role.managed[each.value.role_name].id
  policy = jsonencode(each.value.document)
}
