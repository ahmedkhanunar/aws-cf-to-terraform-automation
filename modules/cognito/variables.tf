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

variable "tags" {
  type    = map(string)
  default = {}
}

variable "environment" {
  type = string
}
