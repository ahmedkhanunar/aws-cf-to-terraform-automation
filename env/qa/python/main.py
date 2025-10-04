import json
import os
import requests
from botocore.exceptions import ClientError

from modules.cloudformation_utils import list_stacks, list_stack_resources
from modules.s3_module import get_s3_config
from modules.dynamodb_module import get_dynamodb_config
from modules.lambda_module import get_lambda_config

from modules.iam_role_module import (
    get_iam_role_config, get_iam_user_config, get_iam_group_config,
    get_iam_managed_policy_config
)

from modules.secrets_manager_module import get_secret_config
from modules.sns_module import get_sns_topic_config
from modules.vpc_module import get_vpc_config, extract_flat_resources
from modules.api_module import get_api_config, flatten_api_gateway_resources
from modules.cloudfront_module import get_cloudfront_config
from modules.cloudtrail_module import get_cloudtrail_config
from modules.cloudwatch_module import get_log_group_config

from modules.cognito_module import (
    get_user_pool_config,
    get_user_pool_client_config,
    get_identity_pool_config,
    find_user_pool_for_client
)


from modules.config_module import (
    get_config_recorder_config,
    get_config_recorder_status,
    get_delivery_channel_config,
    get_delivery_channel_status,
    get_config_rule_config,
    get_rule_compliance
)

from modules.kms_module import get_kms_key_config
from modules.lambda_layer_module import get_lambda_layer_config_by_arn
from modules.waf_module import get_web_acl_config, get_ip_set_config


# -----------------------
# Main Script
# -----------------------
def main():
    all_buckets = {}
    all_dynamodb = {}
    all_lambdas = {}
    all_roles = {}
    all_users = {}
    all_groups = {}
    all_managed_policies = {}
    all_secrets = {}
    all_sns_topics = {}
    all_vpcs = {}

    # For storing API Gateway data
    all_apis = {}  
    all_resources = {}
    all_methods = {}
    all_stages = {}

    all_cloudfront_dists = {}
    all_cloudtrails = {}
    all_log_groups = {}


    all_user_pools = {}
    all_user_pool_clients = {}
    all_identity_pools = {}

    all_config_recorders = {}
    all_delivery_channels = {}
    all_config_rules = {}
    all_kms_keys = {}
    all_lambda_layers = {}
    all_waf = {"web_acls": {}, "ip_sets": {}}

    stacks = list_stacks()
    # print(f"📦 Found {len(stacks)} stacks")

    for stack in stacks:
        # print(f"\n🔍 Processing stack: {stack}")
        resources = list_stack_resources(stack)

        for res in resources:
            rtype = res["ResourceType"]
            rid = res["PhysicalResourceId"]
            status = res["ResourceStatus"]
            
            # Skip deleted resources
            if status == "DELETE_COMPLETE":
                continue

            if rtype == "AWS::S3::Bucket":
                # print(f"   → Found bucket: {rid}")
                bucket_config = get_s3_config(rid)
                if bucket_config:
                    all_buckets[rid] = bucket_config

            elif rtype == "AWS::DynamoDB::Table":
                # print(f"   → Found DynamoDB table: {rid}")
                table_config = get_dynamodb_config(rid)
                if table_config:
                    all_dynamodb[rid] = table_config

            elif rtype == "AWS::Lambda::Function":
                # print(f"   → Found Lambda function: {rid}")
                lambda_config = get_lambda_config(rid)
                if lambda_config:
                    all_lambdas[rid] = lambda_config

            elif rtype == "AWS::IAM::Role":
                # print(f"   → Found IAM Role: {rid}")
                continue
                role_config = get_iam_role_config(rid)
                if role_config:
                    all_roles[rid] = role_config

            elif rtype == "AWS::IAM::User":
                # print(f"   → Found IAM User: {rid}")
                user_config = get_iam_user_config(rid)
                if user_config:
                    all_users[rid] = user_config

            elif rtype == "AWS::IAM::Group":
                # print(f"   → Found IAM Group: {rid}")
                group_config = get_iam_group_config(rid)
                if group_config:
                    all_groups[rid] = group_config

            elif rtype == "AWS::IAM::Policy":
                # print(f"   → Found IAM Policy: {rid}")
                policy_config = get_iam_managed_policy_config(rid)
                if policy_config:
                    all_managed_policies[rid] = policy_config
            elif rtype == "AWS::SecretsManager::Secret":
                # print(f"   → Found Secret: {rid}")
                secret_config = get_secret_config(rid)
                if secret_config:
                    all_secrets[rid] = secret_config

            elif rtype == "AWS::SNS::Topic":
                # print(f"   → Found SNS Topic: {rid}")
                topic_config = get_sns_topic_config(rid)
                if topic_config:
                    all_sns_topics[rid] = topic_config

            elif rtype == "AWS::EC2::VPC":
                # print(f"   → Found VPC: {rid}")
                vpc_config = get_vpc_config(rid)
                if vpc_config:
                    all_vpcs[rid] = vpc_config

            # elif rtype == "AWS::ApiGateway::RestApi":  # API Gateway Rest API
                # print(f"   → Found API Gateway API: {rid}")
                # api_config = get_api_config(rid)
                # if api_config:
                #     all_apis[rid] = api_config["api"]
                #     all_resources[rid] = api_config["resources"]
                #     all_methods[rid] = api_config["methods"]
                #     all_stages[rid] = api_config["stages"]
            
            # elif rtype == "AWS::CloudFront::Distribution":
            #     print(f"   → Found CloudFront Distribution: {rid}")
            #     dist_config = get_cloudfront_config(rid)
            #     if dist_config:
            #         all_cloudfront_dists[rid] = dist_config

            elif rtype == "AWS::CloudTrail::Trail":
                # print(f"   → Found CloudTrail: {rid}")
                trail_config = get_cloudtrail_config(rid)
                if trail_config:
                    all_cloudtrails[rid] = trail_config

            elif rtype == "AWS::Logs::LogGroup":
                # print(f"   → Found CloudWatch Log Group: {rid}")
                log_group_config = get_log_group_config(rid)
                if log_group_config:
                    all_log_groups[rid] = log_group_config

            elif rtype == "AWS::Cognito::UserPool":
                user_pool_config = get_user_pool_config(rid)
                if user_pool_config:
                    all_user_pools[rid] = user_pool_config

            elif rtype == "AWS::Cognito::UserPoolClient":
                pool_id = find_user_pool_for_client(rid)
                if pool_id:
                    client_config = get_user_pool_client_config(pool_id, rid)
                    if client_config:
                        all_user_pool_clients[rid] = client_config
                else:
                    print(f"⚠️ Skipped UserPoolClient {rid} (no parent pool found)")

            elif rtype == "AWS::Cognito::IdentityPool":
                identity_pool_config = get_identity_pool_config(rid)
                if identity_pool_config:
                    all_identity_pools[rid] = identity_pool_config

            elif rtype == "AWS::Config::ConfigurationRecorder":
                recorder_config = get_config_recorder_config(rid)
                recorder_status = get_config_recorder_status(rid)
                if recorder_config:
                    all_config_recorders[rid] = {
                        "config": recorder_config,
                        "status": recorder_status
                    }

            elif rtype == "AWS::Config::DeliveryChannel":
                channel_config = get_delivery_channel_config(rid)
                channel_status = get_delivery_channel_status(rid)
                if channel_config:
                    all_delivery_channels[rid] = {
                        "config": channel_config,
                        "status": channel_status
                    }

            elif rtype == "AWS::Config::ConfigRule":
                rule_config = get_config_rule_config(rid)
                rule_status = get_rule_compliance(rid)
                if rule_config:
                    all_config_rules[rid] = {
                        "config": rule_config,
                        "compliance": rule_status
                    }

            elif rtype == "AWS::KMS::Key":
                # print(f"   → Found KMS Key: {rid}")
                kms_config = get_kms_key_config(rid)
                if kms_config:
                    all_kms_keys[rid] = kms_config

            elif rtype == "AWS::Lambda::LayerVersion":
                # print(f"   → Found Lambda Layer: {rid}")
                layer_config = get_lambda_layer_config_by_arn(rid)
                if layer_config:
                    all_lambda_layers[rid] = layer_config

            elif rtype == "AWS::WAFv2::WebACL":
                print(f"   → Found WAFv2 WebACL: {rid}")
                web_acl_config = get_web_acl_config(rid)
                if web_acl_config:
                    all_waf["web_acls"][rid] = web_acl_config

            elif rtype == "AWS::WAFv2::IPSet":
                print(f"   → Found WAFv2 IPSet: {rid}")
                ip_set_config = get_ip_set_config(rid)
                if ip_set_config:
                    all_waf["ip_sets"][rid] = ip_set_config

    # Save outputs
    if all_buckets:
        with open("../s3.auto.tfvars.json", "w") as f:
            json.dump({"buckets": all_buckets}, f, indent=2)
        print("✅ Exported S3 buckets → s3.auto.tfvars.json")

    if all_dynamodb:
        with open("../dynamodb.auto.tfvars.json", "w") as f:
            json.dump({"dynamodb_tables": all_dynamodb}, f, indent=2)
        print("✅ Exported DynamoDB tables → dynamodb.auto.tfvars.json")

    if all_lambdas:
        with open("../lambda.auto.tfvars.json", "w") as f:
            json.dump({"functions": all_lambdas}, f, indent=2)
        print("✅ Exported Lambdas → lambda.auto.tfvars.json")

    if all_roles:
        with open("../iam_roles.auto.tfvars.json", "w") as f:
            json.dump({"roles": all_roles}, f, indent=2)
        print("✅ Exported IAM Roles → iam_roles.auto.tfvars.json")

    if all_users:
        with open("../iam_users.auto.tfvars.json", "w") as f:
            json.dump({"users": all_users}, f, indent=2)
        print("✅ Exported IAM Users → iam_users.auto.tfvars.json")

    if all_groups:
        with open("../iam_groups.auto.tfvars.json", "w") as f:
            json.dump({"groups": all_groups}, f, indent=2)
        print("✅ Exported IAM Groups → iam_groups.auto.tfvars.json")

    if all_managed_policies:
        with open("../iam_policies.auto.tfvars.json", "w") as f:
            json.dump({"policies": all_managed_policies}, f, indent=2)
        print("✅ Exported IAM Managed Policies → iam_policies.auto.tfvars.json")

    if all_secrets:
        with open("../secrets.auto.tfvars.json", "w") as f:
            json.dump({"secrets": all_secrets}, f, indent=2)
        print("✅ Exported Secrets → secrets.auto.tfvars.json")

    if all_sns_topics:
        with open("../sns.auto.tfvars.json", "w") as f:
            json.dump({"topics": all_sns_topics}, f, indent=2)
        print("✅ Exported SNS topics → sns.auto.tfvars.json")

    if all_vpcs:
        flat = extract_flat_resources({"vpcs": all_vpcs})
        with open("../vpc.auto.tfvars.json", "w") as f:
            json.dump(flat, f, indent=2)
        print("✅ Exported VPCs → vpc.auto.tfvars.json")

    # API Gateway Data Export
    # if all_apis:
    #     # Flatten the API Gateway data
    #     flattened_api_data = flatten_api_gateway_resources({
    #         "apis": all_apis,
    #         "resources": all_resources,
    #         "methods": all_methods,
    #         "stages": all_stages
    #     })
    #     with open("../api_gateway.auto.tfvars.json", "w") as f:
    #         json.dump(flattened_api_data, f, indent=2)
    #     print("✅ Exported API Gateway data → api_gateway.auto.tfvars.json")

    # if all_cloudfront_dists:
    #     with open("../cloudfront.auto.tfvars.json", "w") as f:
    #         json.dump({"distributions": all_cloudfront_dists}, f, indent=2)
    #     print("✅ Exported CloudFront Distributions → cloudfront.auto.tfvars.json")

    if all_cloudtrails:
        with open("../cloudtrail.auto.tfvars.json", "w") as f:
            json.dump({"cloudtrails": all_cloudtrails}, f, indent=2)
        print("✅ Exported CloudTrails → cloudtrail.auto.tfvars.json")

    if all_log_groups:
        with open("../cloudwatch.auto.tfvars.json", "w") as f:
            json.dump({"log_groups": all_log_groups}, f, indent=2)
        print("✅ Exported CloudWatch Log Groups → cloudwatch.auto.tfvars.json")

    if any([all_user_pools, all_user_pool_clients, all_identity_pools]):
        cognito_data = {
            "user_pools": all_user_pools,
            "user_pool_clients": all_user_pool_clients,
            "identity_pools": all_identity_pools
        }
        with open("../cognito.auto.tfvars.json", "w") as f:
            json.dump(cognito_data, f, indent=2)
        print("✅ Exported Cognito resources → cognito.auto.tfvars.json")

    if any([all_config_recorders, all_delivery_channels, all_config_rules]):
        config_data = {
            "recorders": all_config_recorders,
            "delivery_channels": all_delivery_channels,
            "config_rules": all_config_rules
        }
        with open("../config.auto.tfvars.json", "w") as f:
            json.dump(config_data, f, indent=2)
        print("✅ Exported AWS Config → config.auto.tfvars.json")

    if all_kms_keys:
        kms_aliases = {
            config["alias_name"]: key_id
            for key_id, config in all_kms_keys.items()
            if config.get("alias_name")  # Ensure alias is not None
        }

        # Create final structure for KMS keys and aliases
        final_kms_data = {
            "kms_keys": all_kms_keys,
            "kms_aliases": kms_aliases
        }

        # Write the data to the final file
        with open("../kms.auto.tfvars.json", "w") as f:
            json.dump(final_kms_data, f, indent=2)

        print("✅ Exported KMS Keys and Aliases → kms.auto.tfvars.json")

    if all_lambda_layers:
        with open("../lambda_layers.auto.tfvars.json", "w") as f:
            json.dump({"lambda_layers": all_lambda_layers}, f, indent=2)
        print("✅ Exported Lambda Layers → lambda_layers.auto.tfvars.json")

    if any([all_waf["web_acls"], all_waf["ip_sets"]]):
        with open("../waf.auto.tfvars.json", "w") as f:
            json.dump(all_waf, f, indent=2)
        print("✅ Exported WAF resources → waf.auto.tfvars.json")


if __name__ == "__main__":
    main()

