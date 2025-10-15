variable "environment" {
  type    = string
  default = "qa"
}

variable "resources" {
  description = "Map keyed by resource id to API Gateway resource configs"
  type        = any
  default     = {}
}

variable "methods" {
  description = "Map keyed by resourceId|httpMethod to API Gateway method configs"
  type        = any
  default     = {}
}

variable "method_responses" {
  description = "Map keyed by resourceId|httpMethod|statusCode to method response configs"
  type        = any
  default     = {}
}

variable "integrations" {
  description = "Map keyed by resourceId|httpMethod to integration configs"
  type        = any
  default     = {}
}

variable "integration_responses" {
  description = "Map keyed by resourceId|httpMethod|statusCode to integration response configs"
  type        = any
  default     = {}
}

variable "deployments" {
  description = "Map keyed by deployment id to deployment configs"
  type        = any
  default     = {}
}

variable "base_path_mappings" {
  description = "Map keyed by domain|basePath to base path mapping configs"
  type        = any
  default     = {}
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

variable "roles" {
  description = "Map of IAM Role configurations (auto-generated)"
  type = map(object({
    role_name                 = string
    path                      = optional(string, "/")
    assume_role_policy        = any
    description               = optional(string)
    max_session_duration      = optional(number)
    permissions_boundary      = optional(string)
    tags                      = optional(map(string))
    attached_managed_policies = optional(list(string), [])
    inline_policies           = optional(map(string), {})  # JSON strings
  }))
  default = {}
}

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

variable "state_machines" {
  description = "Map of Step Functions state machine configurations"
  type = map(object({
    name                   = string
    definition             = string
    role_arn               = string
    type                   = optional(string)
    logging_configuration  = optional(object({
      include_execution_data = optional(bool)
      level                  = optional(string)
      log_destination        = optional(string)
    }))
    tracing_configuration  = optional(object({
      enabled = optional(bool)
    }))
    tags = optional(map(string))
  }))
  default = {}
}


variable "rest_apis" {
  description = "API Gateway RestApis keyed by CFN rid"
  type = map(object({
    id                        = string
    name                      = string
    description               = optional(string)
    api_key_source            = optional(string)
    endpoint_configuration    = optional(object({
      types = optional(list(string))
      ipAddressType = optional(string)
    }))
    binary_media_types        = optional(list(string))
    minimum_compression_size  = optional(number)
    policy                    = optional(string)
    tags                      = optional(map(string))
    version                   = optional(string)
    warnings                  = optional(list(string))
  }))
  default = {}
}

variable "account" {
  description = "API Gateway account map keyed by rid"
  type = map(object({
    cloudwatchRoleArn = optional(string)
    throttleSettings = optional(object({
      burstLimit = optional(number)
      rateLimit  = optional(number)
    }))
    features = optional(list(string))
    account_id = optional(string)
  }))
  default = {}
}

variable "domain_names" {
  description = "API Gateway domain names keyed by domain name"
  type = map(object({
    domain_name                   = string
    certificate_arn               = optional(string)
    certificate_name              = optional(string)
    certificate_upload_date       = optional(string)
    distribution_domain_name      = optional(string)
    distribution_hosted_zone_id   = optional(string)
    regional_domain_name          = optional(string)
    regional_hosted_zone_id       = optional(string)
    regional_certificate_arn      = optional(string)
    regional_certificate_name     = optional(string)
    endpoint_configuration        = optional(object({
      types = optional(list(string))
    }))
    mutual_tls_authentication     = optional(object({
      truststore_uri     = optional(string)
      truststore_version = optional(string)
    }))
    security_policy              = optional(string)
    tags                         = optional(map(string))
  }))
  default = {}
}

variable "stages" {
  description = "API Gateway stages keyed by CFN rid"
  type = map(object({
    rest_api_id           = string
    stage_name           = string
    deployment_id        = optional(string)
    description          = optional(string)
    cache_cluster_enabled = optional(bool)
    cache_cluster_size   = optional(string)
    variables            = optional(map(string))
    documentation_version = optional(string)
    tracing_enabled      = optional(bool)
    access_log_settings  = optional(object({
      destinationArn = optional(string)
      format         = optional(string)
    }))
    canary_settings      = optional(object({
      percent_traffic = optional(number)
      deployment_id   = optional(string)
      stage_variable_overrides = optional(map(string))
      use_stage_cache = optional(bool)
    }))
    tags                 = optional(map(string))
    web_acl_arn          = optional(string)
    method_settings      = optional(list(object({
      resource_path = optional(string)
      http_method   = optional(string)
      throttling_burst_limit = optional(number)
      throttling_rate_limit  = optional(number)
      caching_enabled         = optional(bool)
      cache_ttl_in_seconds   = optional(number)
      cache_data_encrypted   = optional(bool)
      require_authorization_for_cache_control = optional(bool)
      unauthorized_cache_control_header_strategy = optional(string)
    })), [])
  }))
  default = {}
}