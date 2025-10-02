variable "route_tables" {
  type = map(object({
    RouteTableId      = string
    VpcId             = string
    OwnerId           = string
    PropagatingVgws   = optional(list(string))
    Tags              = optional(list(object({
      Key   = string
      Value = string
    })))
    Routes = optional(list(object({
      DestinationCidrBlock       = string
      GatewayId                  = optional(string)
      NatGatewayId               = optional(string)
      TransitGatewayId           = optional(string)
      EgressOnlyGatewayId        = optional(string)
      InstanceId                 = optional(string)
      NetworkInterfaceId         = optional(string)
      VpcPeeringConnectionId     = optional(string)
      Origin                     = optional(string)
      State                      = optional(string)
    })))
    Associations = optional(list(object({
      Main                      = optional(bool)
      RouteTableAssociationId  = optional(string)
      RouteTableId             = optional(string)
      SubnetId                 = optional(string)
      GatewayId                = optional(string)
      AssociationState         = optional(object({
        State = optional(string)
      }))
    })))
  }))
}


variable "tags" {
  type    = map(string)
  default = {}
}

variable "environment" {
  type = string
}
