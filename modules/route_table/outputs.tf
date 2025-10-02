output "route_table_ids" {
  value = { for k, v in aws_route_table.managed : k => v.id }
}
