output "nat_gateways" {
  description = "Details of the NAT Gateways"
  value = {
    for id, nat in var.nat_gateways : id => {
      nat_gateway_id = nat.nat_gateway_id
      subnet_id      = nat.subnet_id
      state          = nat.state
      elastic_ip     = nat.elastic_ip
      tags           = nat.tags
    }
  }
}
