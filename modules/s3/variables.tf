variable "environment" {
  type = string
}

variable "tags" {
  type    = map(string)
  default = {}
}

variable "buckets" {
  description = "Map of S3 bucket configurations"
  type = map(object({
    bucket            = string
    region            = string
    creation_date     = string
    versioning_status = optional(string, "Disabled")  # <-- Add this
  }))
  default = {}
}
