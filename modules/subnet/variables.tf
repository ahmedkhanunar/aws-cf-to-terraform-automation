variable "subnets" {
  type = map(object({
    vpc_id                  = string
    cidr_block              = string
    availability_zone_id    = string
    map_public_ip_on_launch = optional(bool)
    tags                    = optional(list(object({ Key = string, Value = string })))
  }))
}

variable "tags" {
  type    = map(string)
  default = {}
}

variable "environment" {
  type = string
}
