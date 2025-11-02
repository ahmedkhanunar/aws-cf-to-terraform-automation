output "cloudfront_distributions" {
  description = "CloudFront distributions created"
  value = {
    for k, v in aws_cloudfront_distribution.managed :
    k => {
      id           = v.id
      arn          = v.arn
      domain_name  = v.domain_name
      status       = v.status
    }
  }
}

output "cloudfront_distribution_ids" {
  description = "CloudFront distribution IDs"
  value = [for k, v in aws_cloudfront_distribution.managed : v.id]
}

