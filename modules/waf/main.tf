resource "aws_wafv2_web_acl" "managed" {
  for_each = var.web_acls

  name        = each.value.name
  description = length(each.value.description) > 0 && length(each.value.description) <= 256 ? each.value.description : "Default Description"
  scope       = each.value.scope

  default_action {
    allow {}
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "${each.value.name}-metrics"
    sampled_requests_enabled   = true
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      rule,
      captcha_config,
      challenge_config,
      association_config,
      token_domains,
      visibility_config,
      description
    ]
  }
}
