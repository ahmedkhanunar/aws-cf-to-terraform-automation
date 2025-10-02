variable "internet_gateways" {
  type = map(object({
    Attachments = list(object({
      VpcId = string
    }))
    tags = optional(list(object({ Key = string, Value = string })))
  }))
}


variable "tags" {
  type    = map(string)
  default = {}
}

variable "environment" {
  type = string
}
