# -------------------------------------
# Cognito User Pools
# -------------------------------------
resource "aws_cognito_user_pool" "managed" {
  for_each = var.user_pools

  name                       = each.value.name
  alias_attributes           = try(each.value.alias_attributes, [])
  auto_verified_attributes   = try(each.value.auto_verified_attributes, [])
  mfa_configuration          = try(each.value.mfa_configuration, "OFF")
  email_verification_subject = try(each.value.email_verification_subject, null)
  email_verification_message = try(each.value.email_verification_message, null)
  sms_verification_message   = try(each.value.sms_verification_message, null)

  password_policy {
    minimum_length                   = try(each.value.policies.PasswordPolicy.MinimumLength, 8)
    require_uppercase                = try(each.value.policies.PasswordPolicy.RequireUppercase, true)
    require_lowercase                = try(each.value.policies.PasswordPolicy.RequireLowercase, true)
    require_numbers                  = try(each.value.policies.PasswordPolicy.RequireNumbers, true)
    require_symbols                  = try(each.value.policies.PasswordPolicy.RequireSymbols, true)
    temporary_password_validity_days = try(each.value.policies.PasswordPolicy.TemporaryPasswordValidityDays, 7)
  }

  tags = merge(
    var.tags,
    try(each.value.tags, {}),
    {
      ManagedBy   = "terraform",
      Imported    = "true",
      Environment = var.environment
    }
  )


  lifecycle {
    ignore_changes = [
      tags_all,
      username_attributes,
      account_recovery_setting,
      deletion_protection,
      email_configuration,
      schema,
      lambda_config,
      admin_create_user_config,
      user_attribute_update_settings,
      sign_in_policy,
      auto_verified_attributes,
      tags
    ]
  }
}

# -------------------------------------
# Cognito User Pool Clients
# -------------------------------------
resource "aws_cognito_user_pool_client" "managed" {
  for_each = var.user_pool_clients

  name         = each.value.name
  user_pool_id = each.value.user_pool_id

  generate_secret                     = try(each.value.generate_secret, false)
  refresh_token_validity              = try(each.value.refresh_token_validity, 30)
  access_token_validity               = try(each.value.access_token_validity, 60)
  id_token_validity                   = try(each.value.id_token_validity, 60)
  # token_validity_units                = try(each.value.token_validity_units, null)
  supported_identity_providers        = try(each.value.supported_identity_providers, [])
  allowed_oauth_flows                 = try(each.value.allowed_oauth_flows, [])
  allowed_oauth_scopes                = try(each.value.allowed_oauth_scopes, [])
  allowed_oauth_flows_user_pool_client = try(each.value.allowed_oauth_flows_user_pool_client, false)
  callback_urls                       = try(each.value.callback_urls, [])
  logout_urls                         = try(each.value.logout_urls, [])
  explicit_auth_flows                 = try(each.value.explicit_auth_flows, [])

  lifecycle {
    ignore_changes = [token_validity_units]
  }
}

# -------------------------------------
# Cognito Identity Pools
# -------------------------------------
resource "aws_cognito_identity_pool" "managed" {
  for_each = var.identity_pools

  identity_pool_name                = each.value.identity_pool_name
  allow_unauthenticated_identities = try(each.value.allow_unauthenticated_identities, false)
  allow_classic_flow               = try(each.value.allow_classic_flow, false)
  developer_provider_name          = try(each.value.developer_provider_name, null)
  supported_login_providers        = try(each.value.supported_login_providers, null)
  # cognito_identity_providers       = try(each.value.cognito_identity_providers, null)
  saml_provider_arns               = try(each.value.saml_provider_arns, null)
  openid_connect_provider_arns     = try(each.value.openid_connect_provider_arns, null)

  tags = merge(
    var.tags,
    try(each.value.tags, {}),
    {
      ManagedBy   = "terraform",
      Imported    = "true",
      Environment = var.environment
    }
  )


  lifecycle {
    ignore_changes = [tags_all, tags]
  }
}
