variable "recorders" {
  description = "AWS Config recorders map"
  type = map(object({
    config = object({
      name           = string
      roleARN        = string
      recordingGroup = optional(any)
      recordingMode  = optional(any)
      recordingScope = optional(string)
    })
    status = optional(any)
  }))
}

variable "delivery_channels" {
  description = "AWS Config delivery channels map"
  type = map(object({
    config = object({
      name                             = string
      s3BucketName                     = string
      s3KeyPrefix                      = optional(string)
      snsTopicARN                      = optional(string)
      configSnapshotDeliveryProperties = optional(object({
        deliveryFrequency = string
      }))
    })
    status = optional(any)
  }))
}

variable "tags" {
  type        = map(string)
  default     = {}
  description = "Common tags to apply to resources"
}

variable "environment" {
  type        = string
  description = "Environment label (e.g., dev, prod)"
  default     = "dev"
}
