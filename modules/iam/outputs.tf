output "iam_roles" {
  description = "IAM Roles created"
  value = {
    for k, v in aws_iam_role.managed :
    k => {
      name = v.name
      arn  = v.arn
      id   = v.id
    }
  }
}
