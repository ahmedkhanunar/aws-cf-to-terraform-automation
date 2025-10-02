resource "aws_route_table" "managed" {
  for_each = var.route_tables

  vpc_id = each.value.VpcId

  tags = merge(
    var.tags,
    { ManagedBy = "terraform", Imported = "true", Environment = var.environment }
  )

  lifecycle {
    ignore_changes = [tags_all, tags]
  }
}

# ROUTES (flattened per route)
resource "aws_route" "routes" {
  for_each = merge(
    [
      for rt_key, rt in var.route_tables :
      {
        for idx, route in coalesce(rt.Routes, []) :
        "${rt_key}-${idx}" => {
          route_table_key = rt_key
          route           = route
        }
      }
    ]...
  )

  route_table_id             = aws_route_table.managed[each.value.route_table_key].id
  destination_cidr_block     = each.value.route.DestinationCidrBlock
  gateway_id                 = try(each.value.route.GatewayId, null)
  nat_gateway_id             = try(each.value.route.NatGatewayId, null)
  transit_gateway_id         = try(each.value.route.TransitGatewayId, null)
  egress_only_gateway_id     = try(each.value.route.EgressOnlyGatewayId, null)
  network_interface_id       = try(each.value.route.NetworkInterfaceId, null)
  vpc_peering_connection_id  = try(each.value.route.VpcPeeringConnectionId, null)


  # You can uncomment this if needed:
  # instance_id               = try(each.value.route.instance_id, null)
}

# ASSOCIATIONS (flattened per association)
resource "aws_route_table_association" "associations" {
  for_each = merge(
    [
      for rt_key, rt in var.route_tables :
      {
        for idx, assoc in coalesce(rt.Associations, []) :
        "${rt_key}-${idx}" => {
          route_table_key = rt_key
          association     = assoc
        } if !try(assoc.Main, false) # <<< FILTER OUT "Main": true associations
      }
    ]...
  )

  route_table_id = aws_route_table.managed[each.value.route_table_key].id
  subnet_id      = try(each.value.association.SubnetId, null)
  gateway_id     = try(each.value.association.GatewayId, null)

  lifecycle {
    ignore_changes = [subnet_id]  # Ignore changes to subnet_id
  }
}
