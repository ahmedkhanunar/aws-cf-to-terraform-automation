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
from modules.events_module import get_event_rule_config
from modules.sqs_module import get_sqs_queue_config_by_physical_resource_id
from modules.stepfunctions_module import get_state_machine_config_by_arn
from modules.apigateway_module import (
    extract_rest_api_id_from_rid,
    get_rest_api_config_by_id,
    get_account as get_apigw_account,
    get_domain_name_config,
    list_rest_apis,
    list_stages_for_api,
    parse_stage_from_rid,
    find_stage_config,
    list_resources_for_api,
    find_resources_by_ids,
    list_deployments_for_api,
    get_deployment_by_id,
    list_base_path_mappings_for_domain,
    get_base_path_mapping,
)


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

    # For storing API Gateway data (keyed by CFN PhysicalResourceId rid)
    apigw_rest_apis = {}
    apigw_account = {}
    apigw_domain_names = {}
    apigw_stages = {}
    apigw_resources = {}
    apigw_methods = {}
    apigw_method_responses = {}
    apigw_integrations = {}
    apigw_integration_responses = {}
    apigw_deployments = {}
    apigw_base_path_mappings = {}

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
    all_event_rules = {}
    all_sqs_queues = {}
    all_state_machines = {}

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
                # print(f"   → Found WAFv2 WebACL: {rid}")
                web_acl_config = get_web_acl_config(rid)
                if web_acl_config:
                    all_waf["web_acls"][rid] = web_acl_config

            elif rtype == "AWS::WAFv2::IPSet":
                # print(f"   → Found WAFv2 IPSet: {rid}")
                ip_set_config = get_ip_set_config(rid)
                if ip_set_config:
                    all_waf["ip_sets"][rid] = ip_set_config

            elif rtype == "AWS::Events::Rule":
                # print(f"   → Found EventBridge Rule: {rid}")
                event_rule_config = get_event_rule_config(rid)
                if event_rule_config:
                    all_event_rules[rid] = event_rule_config

            elif rtype == "AWS::SQS::Queue":
                # print(f"   → Found SQS Queue: {rid}")
                sqs_queue_config = get_sqs_queue_config_by_physical_resource_id(rid)
                if sqs_queue_config:
                    all_sqs_queues[rid] = sqs_queue_config

            elif rtype == "AWS::StepFunctions::StateMachine":
                sm_config = get_state_machine_config_by_arn(rid)
                if sm_config:
                    # use ARN as key
                    all_state_machines[rid] = sm_config
            
            elif rtype == "AWS::ApiGateway::RestApi":
                api_id = extract_rest_api_id_from_rid(rid)
                if not api_id:
                    # Try to derive from known APIs
                    apis_all = list_rest_apis()
                    # heuristic: if exactly one API exists, use it
                    if len(apis_all) == 1:
                        api_id = next(iter(apis_all.keys()))
                if api_id:
                    api_cfg = get_rest_api_config_by_id(api_id)
                    if api_cfg:
                        apigw_rest_apis[rid] = api_cfg

            elif rtype == "AWS::ApiGateway::Account":
                acct = get_apigw_account()
                if acct:
                    apigw_account[rid] = acct

            elif rtype == "AWS::ApiGateway::DomainName":
                # CFN rid for domain is the domain name itself
                domain_cfg = get_domain_name_config(rid)
                if domain_cfg:
                    apigw_domain_names[rid] = domain_cfg

            elif rtype == "AWS::ApiGateway::Stage":
                api_id, stage_name = parse_stage_from_rid(rid)
                stage_cfg = None
                if api_id and stage_name:
                    stages = list_stages_for_api(api_id)
                    stage_cfg = stages.get(stage_name)
                elif stage_name:
                    # Search across all APIs
                    all_apis_map = list_rest_apis()
                    found_api_id, stage_cfg = find_stage_config(list(all_apis_map.keys()), stage_name)
                    api_id = found_api_id

                if stage_cfg:
                    # Ensure keys present for import
                    stage_cfg["rest_api_id"] = api_id or stage_cfg.get("rest_api_id")
                    stage_cfg["stage_name"] = stage_name or stage_cfg.get("stage_name")
                    apigw_stages[rid] = stage_cfg

            elif rtype == "AWS::ApiGateway::BasePathMapping":
                # BasePathMapping rid is typically domain_name|base_path or similar
                # Need to extract domain name and base path from the rid
                # The rid might be in format like "api-qa.helloporter.com|(none)" or similar
                parts = rid.split("|") if "|" in rid else [rid, "(none)"]
                domain_name = parts[0]
                base_path = parts[1] if len(parts) > 1 else "(none)"
                
                mapping_cfg = get_base_path_mapping(domain_name, base_path)
                if mapping_cfg:
                    apigw_base_path_mappings[rid] = mapping_cfg
                else:
                    # Fallback: try to find it by listing all mappings for known domains
                    for domain_rid in apigw_domain_names.keys():
                        mappings = list_base_path_mappings_for_domain(domain_rid)
                        for mapping_key, mapping_data in mappings.items():
                            if mapping_key == rid or domain_rid in rid:
                                apigw_base_path_mappings[rid] = mapping_data
                                break

            elif rtype == "AWS::ApiGateway::BasePathMapping":
                # BasePathMapping rid format varies; typically domain_name or domain|path
                # Try to extract domain name and base path
                if "|" in rid:
                    parts = rid.split("|", 1)
                    domain_name = parts[0]
                    base_path = parts[1] if len(parts) > 1 else ""
                else:
                    # Fallback: check all domains
                    domain_name = None
                    for domain_rid in apigw_domain_names.keys():
                        mappings = list_base_path_mappings_for_domain(domain_rid)
                        for mapping_key, mapping_cfg in mappings.items():
                            apigw_base_path_mappings[mapping_key] = mapping_cfg
                    
                if domain_name:
                    mapping_cfg = get_base_path_mapping(domain_name, base_path)
                    if mapping_cfg:
                        key = f"{domain_name}|{base_path if base_path else '(none)'}"
                        apigw_base_path_mappings[key] = mapping_cfg

            elif rtype == "AWS::ApiGateway::Deployment":
                # Deployment rid is deployment ID; need to find which API it belongs to
                # Try to extract from stages that reference it
                found_api_id = None
                for stage_rid, stage_cfg in apigw_stages.items():
                    if stage_cfg.get("deployment_id") == rid:
                        found_api_id = stage_cfg.get("rest_api_id")
                        break
                
                if not found_api_id:
                    # Fallback: check all APIs for this deployment
                    all_apis = list_rest_apis()
                    for api_id in all_apis.keys():
                        deployments = list_deployments_for_api(api_id)
                        if rid in deployments:
                            found_api_id = api_id
                            break
                
                if found_api_id:
                    deployment_cfg = get_deployment_by_id(found_api_id, rid)
                    if deployment_cfg:
                        apigw_deployments[rid] = deployment_cfg

            elif rtype == "AWS::ApiGateway::Resource":
                # rid is the API Gateway Resource ID; need to find its API context
                found = find_resources_by_ids([rid])
                if rid in found:
                    apigw_resources[rid] = found[rid]
                    # expand methods from resource into a flat map
                    methods = found[rid].get("resource_methods", {}) or {}
                    for method_name, method_cfg in methods.items():
                        key = f"{rid}|{method_name}"
                        apigw_methods[key] = {
                            "rest_api_id": found[rid].get("rest_api_id"),
                            "resource_id": rid,
                            "http_method": method_cfg.get("httpMethod", method_name),
                            "authorization": method_cfg.get("authorizationType", "NONE"),
                            "api_key_required": method_cfg.get("apiKeyRequired", False),
                            # Optional shapes; keep loose
                            "request_parameters": method_cfg.get("requestParameters"),
                            "request_models": method_cfg.get("requestModels"),
                        }

                        # Extract method responses
                        method_responses = method_cfg.get("methodResponses", {}) or {}
                        for status_code, resp_cfg in method_responses.items():
                            resp_key = f"{rid}|{method_name}|{status_code}"
                            apigw_method_responses[resp_key] = {
                                "rest_api_id": found[rid].get("rest_api_id"),
                                "resource_id": rid,
                                "http_method": method_cfg.get("httpMethod", method_name),
                                "status_code": status_code,
                                "response_models": resp_cfg.get("responseModels"),
                                "response_parameters": resp_cfg.get("responseParameters"),
                            }

                        # Extract integration
                        integration = method_cfg.get("methodIntegration")
                        if integration:
                            int_key = f"{rid}|{method_name}"
                            apigw_integrations[int_key] = {
                                "rest_api_id": found[rid].get("rest_api_id"),
                                "resource_id": rid,
                                "http_method": method_cfg.get("httpMethod", method_name),
                                "type": integration.get("type"),
                                "integration_http_method": integration.get("httpMethod"),
                                "uri": integration.get("uri"),
                                "credentials": integration.get("credentials"),
                                "request_parameters": integration.get("requestParameters"),
                                "request_templates": integration.get("requestTemplates"),
                                "passthrough_behavior": integration.get("passthroughBehavior"),
                                "timeout_milliseconds": integration.get("timeoutInMillis"),
                                "cache_namespace": integration.get("cacheNamespace"),
                                "cache_key_parameters": integration.get("cacheKeyParameters"),
                            }

                            # Extract integration responses
                            int_responses = integration.get("integrationResponses", {}) or {}
                            for int_status_code, int_resp_cfg in int_responses.items():
                                int_resp_key = f"{rid}|{method_name}|{int_status_code}"
                                apigw_integration_responses[int_resp_key] = {
                                    "rest_api_id": found[rid].get("rest_api_id"),
                                    "resource_id": rid,
                                    "http_method": method_cfg.get("httpMethod", method_name),
                                    "status_code": int_status_code,
                                    "response_parameters": int_resp_cfg.get("responseParameters"),
                                    "response_templates": int_resp_cfg.get("responseTemplates"),
                                    "selection_pattern": int_resp_cfg.get("selectionPattern"),
                                }

    # Save outputs

    # Write API Gateway output keyed by CFN physical IDs
    if any([apigw_rest_apis, apigw_account, apigw_domain_names, apigw_stages, apigw_resources, 
            apigw_methods, apigw_method_responses, apigw_integrations, apigw_integration_responses, 
            apigw_deployments, apigw_base_path_mappings]):
        with open("../api_gateway.auto.tfvars.json", "w") as f:
            json.dump({
                "rest_apis": apigw_rest_apis,
                "account": apigw_account,
                "domain_names": apigw_domain_names,
                "stages": apigw_stages,
                "resources": apigw_resources,
                "methods": apigw_methods,
                "method_responses": apigw_method_responses,
                "integrations": apigw_integrations,
                "integration_responses": apigw_integration_responses,
                "deployments": apigw_deployments,
                "base_path_mappings": apigw_base_path_mappings,
            }, f, indent=2)
        print("✅ Exported API Gateway → api_gateway.auto.tfvars.json")
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

    if all_event_rules:
        with open("../events.auto.tfvars.json", "w") as f:
            json.dump({"event_rules": all_event_rules}, f, indent=2)
        print("✅ Exported EventBridge Rules → events.auto.tfvars.json")

    if all_sqs_queues:
        with open("../sqs.auto.tfvars.json", "w") as f:
            json.dump({"sqs_queues": all_sqs_queues}, f, indent=2)
        print("✅ Exported SQS Queues → sqs.auto.tfvars.json")

    if all_state_machines:
        with open("../stepfunctions.auto.tfvars.json", "w") as f:
            json.dump({"state_machines": all_state_machines}, f, indent=2)
        print("✅ Exported Step Functions State Machines → stepfunctions.auto.tfvars.json")


if __name__ == "__main__":
    main()

