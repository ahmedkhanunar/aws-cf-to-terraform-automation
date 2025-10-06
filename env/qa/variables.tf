variable "environment" {
  type    = string
  default = "qa"
}

variable "tags" {
  type    = map(string)
  default = {}
}

variable "buckets" {
  description = "S3 buckets configuration"
  type = map(object({
    bucket        = string
    region        = string
    creation_date = string
  }))
  default = {}
}

variable "dynamodb_tables" {
  type = map(any)
  default = {}
}

variable "functions" {
  description = "Map of Lambda function configurations (auto-generated)"
  type = map(object({
    handler               = string
    runtime               = string
    role                  = string
    memory_size           = number
    timeout               = number
    dummy_filename        = optional(string)
    environment_variables = optional(map(string))
    layers                = optional(list(string), [])
    architectures         = optional(list(string), ["x86_64"])
    ephemeral_storage     = optional(number)
    tags                  = optional(map(string), {})
    subnet_ids            = optional(list(string), [])
    security_group_ids    = optional(list(string), [])
    publish_version       = optional(bool)
    version               = optional(string)
    aliases = optional(list(object({
      name              = string
      description       = optional(string)
      function_version  = optional(string)
    })), [])
  }))
  default = {}
}

# variable "roles" {
#   type = map(object({
#     role_name                 = string
#     assume_role_policy        = any
#     attached_managed_policies = optional(list(string), [])
#     inline_policies           = optional(map(any), {})
#   }))
# }

variable "secrets" {
  type = map(object({
    name                = string
    description         = string
    kms_key_id          = optional(string)
    rotation_enabled    = optional(bool)
    rotation_lambda_arn = optional(string)
    tags                = optional(list(object({ Key = string, Value = string })))
    # value is excluded intentionally
  }))
}

variable "topics" {
  type = map(object({
    name                        = string
    display_name                = optional(string)
    fifo_topic                  = optional(bool)
    content_based_deduplication = optional(bool)
    # tags                        = optional(list(object({ Key = string, Value = string })))
    subscriptions               = optional(list(object({
      protocol = string
      endpoint = string
      subscription_arn = optional(string)  # <-- Add this line
    })))
    
  }))
}

variable "vpcs" {
  type = map(object({
    cidr_block           = string
    instance_tenancy     = optional(string)
    enable_dns_support   = optional(bool)
    enable_dns_hostnames = optional(bool)
    tags                 = optional(list(object({ Key = string, Value = string })))
  }))
}

variable "subnets" {
  type = map(object({
    vpc_id                  = string
    cidr_block              = string
    availability_zone_id    = string
    map_public_ip_on_launch = optional(bool)
    tags                    = optional(list(object({ Key = string, Value = string })))
  }))
}

variable "internet_gateways" {
  type = map(object({
    Attachments = list(object({
      VpcId = string
    }))
    tags = optional(list(object({ Key = string, Value = string })))
  }))
}

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

variable "network_acls" {
  description = "Map of Network ACLs and their rules/associations"
  type = map(object({
    VpcId     = string
    IsDefault = bool
    Tags      = list(object({
      Key   = string
      Value = string
    }))
    Associations = optional(list(object({
      SubnetId = string
    })), [])
    Entries = optional(list(object({
      CidrBlock   = string
      Egress      = bool
      Protocol    = string
      RuleAction  = string
      RuleNumber  = number
      PortRange   = optional(object({
        From = number
        To   = number
      }))
    })), [])
  }))
}

variable "security_groups" {
  description = "Map of security groups with their rules."
  type = map(object({
    vpc_id           = string
    group_name       = string
    description      = string
    ip_permissions   = optional(list(object({
      ip_protocol    = string
      from_port      = optional(number, null)
      to_port        = optional(number, null)
      ip_ranges      = list(object({ cidr_ip = string }))
      ipv6_ranges    = list(object({ cidr_ipv6 = string }))
      prefix_list_ids = list(string)
    })), [])
    ip_permissions_egress = optional(list(object({
      ip_protocol    = string
      from_port      = optional(number, null)
      to_port        = optional(number, null)
      ip_ranges      = list(object({ cidr_ip = string }))
      ipv6_ranges    = list(object({ cidr_ipv6 = string }))
      prefix_list_ids = list(string)
    })), [])
  }))
}

variable "nat_gateways" {
  description = "Map of NAT Gateway configurations."
  type = map(object({
    nat_gateway_id = string
    subnet_id      = string
    state          = string
    elastic_ip     = string
    tags           = list(object({
      Key   = string
      Value = string
    }))
  }))
  default = {}
}

variable "eips" {
  description = "Map of Elastic IPs and their configurations."
  type = map(object({
    allocation_id  = string
    public_ip      = string
    association_id = optional(string)
    tags           = optional(list(object({
      Key   = string
      Value = string
    })), [])
  }))
}

variable "cloudtrails" {
  type = map(object({
    name                         = string
    s3_bucket_name               = string
    s3_key_prefix                = string
    sns_topic_name               = string
    include_global_service_events = bool
    is_multi_region_trail        = bool
    is_organization_trail        = bool
    log_file_validation_enabled  = bool
    cloud_watch_logs_log_group_arn = string
    cloud_watch_logs_role_arn    = string
    kms_key_id                   = string
    tags                        = list(object({ Key = string, Value = string }))
  }))
}

variable "log_groups" {
  description = "Map of CloudWatch Log Groups to manage"
  type = map(object({
    name              = string
    retention_in_days = optional(number, 90)
    tags              = optional(map(string), {})
  }))
  default = {}
}

variable "user_pools" {
  type = map(object({
    name                       = string
    alias_attributes           = optional(list(string))
    auto_verified_attributes   = optional(list(string))
    mfa_configuration          = optional(string)
    email_verification_subject = optional(string)
    email_verification_message = optional(string)
    sms_verification_message   = optional(string)

    policies = object({
      PasswordPolicy = object({
        MinimumLength                 = optional(number)
        RequireUppercase              = optional(bool)
        RequireLowercase              = optional(bool)
        RequireNumbers                = optional(bool)
        RequireSymbols                = optional(bool)
        TemporaryPasswordValidityDays = optional(number)
      })
    })

    tags = optional(map(string)) # Fix this too — match your JSON which gives a map
  }))
  default = {}
}

variable "user_pool_clients" {
  type = map(object({
    name                              = string
    user_pool_id                      = string
    generate_secret                   = optional(bool)
    refresh_token_validity            = optional(number)
    access_token_validity             = optional(number)
    id_token_validity                 = optional(number)
    token_validity_units              = optional(map(string))
    supported_identity_providers      = optional(list(string))
    allowed_oauth_flows               = optional(list(string))
    allowed_oauth_scopes              = optional(list(string))
    allowed_oauth_flows_user_pool_client = optional(bool)
    callback_urls                     = optional(list(string))
    logout_urls                       = optional(list(string))
    explicit_auth_flows               = optional(list(string))
  }))
  default = {}
}

variable "identity_pools" {
  type = map(object({
    identity_pool_name               = string
    allow_unauthenticated_identities = optional(bool)
    allow_classic_flow               = optional(bool)
    developer_provider_name          = optional(string)
    supported_login_providers        = optional(map(string))
    cognito_identity_providers = optional(list(object({
      client_id                  = string
      provider_name              = string
      server_side_token_check    = optional(bool)
    })))
    saml_provider_arns           = optional(list(string))
    openid_connect_provider_arns = optional(list(string))
    tags                         = optional(list(object({ Key = string, Value = string })))
  }))
  default = {}
}

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



# Add a new variable for API Gateways
variable "apis" {
  description = "Map of API Gateway configurations (auto-generated)"
  type        = map(any)
  default     = {}
}

variable "kms_keys" {
  description = "Map of KMS key configurations"
  type = map(object({
    description              = string
    key_usage               = optional(string)
    customer_master_key_spec = optional(string)
    key_rotation_enabled    = optional(bool)
    deletion_window_in_days = optional(number)
    policy                  = optional(string)
    alias_name              = optional(string)
    tags                    = optional(map(string))
  }))
  default = {}
}

variable "kms_aliases" {
  description = "KMS aliases and their key mappings"
  type        = map(string)
  default     = {}
}

variable "lambda_layers" {
  description = "Map of Lambda layer configurations"
  type = map(object({
    layer_name              = string
    description             = optional(string)
    filename                = optional(string)
    s3_bucket               = optional(string)
    s3_key                  = optional(string)
    s3_object_version       = optional(string)
    compatible_runtimes     = optional(list(string))
    compatible_architectures = optional(list(string))
    license_info            = optional(string)
    tags                    = optional(map(string))
  }))
  default = {}
}

variable "ip_sets" {
  description = "Map of WAFv2 IP sets"
  type = map(object({
    name               = string
    scope              = string
    description        = optional(string)
    ip_address_version = string
    addresses          = optional(list(string))
    tags               = optional(map(string))
  }))
  default = {}
}

variable "web_acls" {
  description = "List of Web ACLs to manage"
  type = map(object({
    name        = string
    id          = string
    arn         = string
    scope       = string
    description = string
    visibility_config = object({
      SampledRequestsEnabled = bool
      CloudWatchMetricsEnabled = bool
      MetricName = string
    })
    tags = map(string)
    ip_sets = list(string)
  }))
}

variable "event_rules" {
  description = "Map of EventBridge rule configurations"
  type = map(object({
    name                = string
    description         = optional(string)
    schedule_expression = optional(string)
    event_pattern       = optional(string)
    role_arn           = optional(string)
    is_enabled         = optional(bool)
    event_bus_name     = optional(string)
    targets            = optional(object({
      target_id = string
      arn       = string
      input     = optional(string)
      input_path = optional(string)
      role_arn  = optional(string)
      ecs_target = optional(object({
        task_definition_arn = string
        launch_type         = string
        network_configuration = object({
          subnets          = list(string)
          security_groups  = list(string)
          assign_public_ip = bool
        })
      }))
    }))
    tags = optional(map(string))
  }))
  default = {}
}

variable "sqs_queues" {
  description = "Map of SQS queue configurations"
  type = map(object({
    name                              = string
    delay_seconds                     = optional(number)
    max_message_size                  = optional(number)
    message_retention_seconds         = optional(number)
    receive_wait_time_seconds         = optional(number)
    visibility_timeout_seconds        = optional(number)
    sqs_managed_sse_enabled          = optional(bool)
    kms_master_key_id                = optional(string)
    kms_data_key_reuse_period_seconds = optional(number)
    fifo_queue                       = optional(bool)
    content_based_deduplication      = optional(bool)
    deduplication_scope              = optional(string)
    fifo_throughput_limit            = optional(string)
    redrive_policy                   = optional(object({
      dead_letter_target_arn = string
      max_receive_count      = number
    }))
    policy                           = optional(string)
    tags                             = optional(map(string))
  }))
  default = {}
}

