module "s3" {
  source      = "../../modules/s3"
  environment = var.environment
  tags        = var.tags
  buckets     = var.buckets
}

module "dynamodb" {
  source          = "../../modules/dynamodb"
  environment     = var.environment
  tags            = var.tags
  dynamodb_tables = var.dynamodb_tables
}

module "lambda" {
  source      = "../../modules/lambda"
  environment = var.environment
  tags        = var.tags
  functions   = var.functions
}

# module "iam" {
#   source = "../../modules/iam"
#   roles  = var.roles
# }

module "secrets" {
  source      = "../../modules/secrets_manager"
  environment = var.environment
  tags        = var.tags
  secrets   = var.secrets
}

module "sns" {
  source      = "../../modules/sns"
  environment = var.environment
  tags        = var.tags
  topics      = var.topics
}

module "vpc" {
  source      = "../../modules/vpc"
  environment = var.environment
  tags        = var.tags
  vpcs        = var.vpcs
}

module "subnet" {
  source      = "../../modules/subnet"
  environment = var.environment
  tags        = var.tags
  subnets     = var.subnets
}


module "internet_gateway" {
  source            = "../../modules/internet_gateway"
  environment       = var.environment
  tags              = var.tags
  internet_gateways = var.internet_gateways
}

module "route_table" {
  source        = "../../modules/route_table"
  environment   = var.environment
  tags          = var.tags
  route_tables  = var.route_tables
}

module "nacl" {
  source       = "../../modules/nacl"
  environment  = var.environment
  tags         = var.tags
  network_acls = var.network_acls
}

module "security_group" {
  source          = "../../modules/security_group"
  environment     = var.environment
  tags            = var.tags
  security_groups = var.security_groups
}

module "nat_gateway" {
  source       = "../../modules/nat_gateway"
  environment  = var.environment
  tags         = var.tags
  nat_gateways = var.nat_gateways
}


module "eip" {
  source       = "../../modules/eip"
  environment  = var.environment
  tags         = var.tags
  eips         = var.eips
}


module "cloudtrail" {
  source       = "../../modules/cloudtrail"
  environment  = var.environment
  tags         = var.tags
  cloudtrails  = var.cloudtrails
}


module "cloudwatch" {
  source       = "../../modules/cloudwatch"
  environment  = var.environment
  tags         = var.tags
  log_groups   = var.log_groups
}

module "cognito" {
  source            = "../../modules/cognito"
  environment       = var.environment
  tags              = var.tags
  user_pools        = var.user_pools
  user_pool_clients = var.user_pool_clients
  identity_pools    = var.identity_pools
}

module "config" {
  source            = "../../modules/config"
  environment       = var.environment
  tags              = var.tags
  recorders         = var.recorders
  delivery_channels = var.delivery_channels
}

module "kms" {
  source      = "../../modules/kms"
  environment = var.environment
  tags        = var.tags
  kms_keys    = var.kms_keys
  kms_aliases = var.kms_aliases
}

module "lambda_layers" {
  source        = "../../modules/lambda_layer"
  environment   = var.environment
  tags          = var.tags
  lambda_layers = var.lambda_layers
}



# # module "api_gateway" {
# #   source      = "../../modules/api_gateway"
# #   environment = var.environment
# #   tags        = var.tags
# #   apis        = var.apis
# # }

