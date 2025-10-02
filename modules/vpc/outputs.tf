output "vpc_ids" {
  value = { for k, v in aws_vpc.managed : k => v.id }
}
