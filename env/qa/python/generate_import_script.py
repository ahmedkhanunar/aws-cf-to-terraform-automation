import json
import os
import re
import stat

modules = [
    {
        "json_file": "../s3.auto.tfvars.json",
        "json_key": "buckets",
        "tf_module": "module.s3",
        "tf_files": ["../../../modules/s3/main.tf"],
        "resources": {
            "aws_s3_bucket.managed": "",
            "aws_s3_bucket_versioning.managed": "",
            "aws_s3_bucket_server_side_encryption_configuration.managed": "",
        }
    },
    {
        "json_file": "../dynamodb.auto.tfvars.json",
        "json_key": "dynamodb_tables",
        "tf_module": "module.dynamodb",
        "tf_files": ["../../../modules/dynamodb/main.tf"],
        "resources": {
            "aws_dynamodb_table.managed": ""
        }
    },
    {
        "json_file": "../lambda.auto.tfvars.json",
        "json_key": "functions",
        "tf_module": "module.lambda",
        "tf_files": ["../../../modules/lambda/main.tf"],
        "resources": {
            "aws_lambda_function.managed": "",
            "aws_lambda_alias.alias": "aliases"
        }
    },
    # {
    #     "json_file": "../iam_roles.auto.tfvars.json",
    #     "json_key": "roles",
    #     "tf_module": "module.iam",
    #     "tf_files": ["../../../modules/iam/main.tf"],
    #     "resources": {
    #         "aws_iam_role.managed": "",
    #         "aws_iam_role_policy_attachment.managed": "attached_managed_policies",
    #         "aws_iam_role_policy.inline": "inline_policies"
    #     }
    # },
    {
        "json_file": "../secrets.auto.tfvars.json",
        "json_key": "secrets",
        "tf_module": "module.secrets",
        "tf_files": ["../../../modules/secrets_manager/main.tf"],
        "resources": {
            "aws_secretsmanager_secret.managed": ""
        }
    },
    {
        "json_file": "../sns.auto.tfvars.json",
        "json_key": "topics",
        "tf_module": "module.sns",
        "tf_files": ["../../../modules/sns/main.tf"],
        "resources": {
            "aws_sns_topic.managed": "",
            "aws_sns_topic_subscription.managed": "subscriptions"
        }
    },
    {
        "json_file": "../vpc.auto.tfvars.json",
        "json_key": "vpcs",
        "tf_module": "module.vpc",
        "tf_files": ["../../../modules/vpc/main.tf"],
        "resources": {
            "aws_vpc.managed": ""
        }
    },
    {
        "json_file": "../vpc.auto.tfvars.json",
        "json_key": "subnets",
        "tf_module": "module.subnet",
        "tf_files": ["../../../modules/subnet/main.tf"],
        "resources": {
            "aws_subnet.managed": ""
        }
    },
    {
        "json_file": "../vpc.auto.tfvars.json",
        "json_key": "internet_gateways",
        "tf_module": "module.internet_gateway",
        "tf_files": ["../../../modules/internet_gateway/main.tf"],
        "resources": {
            "aws_internet_gateway.managed": ""
        }
    },
    {
        "json_file": "../vpc.auto.tfvars.json",
        "json_key": "route_tables",
        "tf_module": "module.route_table",
        "tf_files": ["../../../modules/route_table/main.tf"],
        "resources": {
            "aws_route_table.managed": "",
            "aws_route.routes": "routes",
            "aws_route_table_association.associations": "associations"
        }
    },
    {
        "json_file": "../vpc.auto.tfvars.json",
        "json_key": "network_acls",
        "tf_module": "module.nacl",
        "tf_files": ["../../../modules/nacl/main.tf"],
        "resources": {
            "aws_network_acl.managed": "",
            "aws_default_network_acl.managed": "",
            "aws_network_acl_rule.rules": "Entries"
        }
    },
    {
        "json_file": "../vpc.auto.tfvars.json",
        "json_key": "security_groups",  # Adjust according to the json structure
        "tf_module": "module.security_group",  # The module where security groups are defined
        "tf_files": ["../../../modules/security_group/main.tf"],  # Adjust path to the tf module
        "resources": {
            "aws_security_group.managed": "",  # Security group resource
            "aws_security_group_rule.ingress": "IngressRules",  # Ingress rules key
            "aws_security_group_rule.egress": "EgressRules",  # Egress rules key
        }
    },
    {
        "json_file": "../vpc.auto.tfvars.json",  # Assuming NAT Gateway info is here
        "json_key": "nat_gateways",  # Key where NAT Gateway data is stored
        "tf_module": "module.nat_gateway",  # Module for NAT Gateway
        "tf_files": ["../../../modules/nat_gateway/main.tf"],  # Path to your NAT Gateway module
        "resources": {
            "aws_nat_gateway.managed": "",  # AWS NAT Gateway resource
        }
    },
    {
        "json_file": "../vpc.auto.tfvars.json", # Update with your correct JSON file
        "json_key": "eips",  # This is the key where your EIP data is stored
        "tf_module": "module.eip",  # Update to match the module name for EIPs
        "tf_files": ["../../../modules/eip/main.tf"],  # Path to your EIP module
        "resources": {
            "aws_eip.managed": ""  # Handle AWS EIP resource
        }
    },
    {
        "json_file": "../cloudtrail.auto.tfvars.json",
        "json_key": "cloudtrails",
        "tf_module": "module.cloudtrail",
        "tf_files": ["../../../modules/cloudtrail/main.tf"],
        "resources": {
            "aws_cloudtrail.managed": ""
        }
    },
    {
        "json_file": "../cloudwatch.auto.tfvars.json",
        "json_key": "log_groups",
        "tf_module": "module.cloudwatch",
        "tf_files": ["../../../modules/cloudwatch/main.tf"],
        "resources": {
            "aws_cloudwatch_log_group.managed": ""
        }
    },
    {
        "json_file": "../cognito.auto.tfvars.json",
        "json_key": "user_pools",
        "tf_module": "module.cognito",
        "tf_files": ["../../../modules/cognito/main.tf"],
        "resources": {
            "aws_cognito_user_pool.managed": ""
        }
    },
    {
        "json_file": "../cognito.auto.tfvars.json",
        "json_key": "user_pool_clients",
        "tf_module": "module.cognito",
        "tf_files": ["../../../modules/cognito/main.tf"],
        "resources": {
            "aws_cognito_user_pool_client.managed": ""
        }
    },
    {
        "json_file": "../config.auto.tfvars.json",
        "json_key": "recorders",
        "tf_module": "module.config",
        "tf_files": ["../../../modules/config/main.tf"],
        "resources": {
            "aws_config_configuration_recorder.managed": "",
            "aws_config_delivery_channel.managed": "../config.auto.tfvars.json:delivery_channels",
            "aws_config_configuration_recorder_status.managed": ""
        }
    },
    {
        "json_file": "../kms.auto.tfvars.json",
        "json_key": "kms_keys",
        "tf_module": "module.kms",
        "tf_files": ["../../../modules/kms/main.tf"],
        "resources": {
            "aws_kms_key.managed": "",
            "aws_kms_alias.managed": "kms_aliases"
        }
    },
    {
        "json_file": "../lambda_layers.auto.tfvars.json",
        "json_key": "lambda_layers",
        "tf_module": "module.lambda_layers",
        "tf_files": ["../../../modules/lambda_layer/main.tf"],
        "resources": {
            "aws_lambda_layer_version.managed": ""
        }
    },
    {
        "json_file": "../waf.auto.tfvars.json",
        "json_key": "web_acls",
        "tf_module": "module.waf",
        "tf_files": ["../../../modules/waf/main.tf"],
        "resources": {
            "aws_wafv2_web_acl.managed": ""
        }
    },
    {
        "json_file": "../events.auto.tfvars.json",
        "json_key": "event_rules",
        "tf_module": "module.events",
        "tf_files": ["../../../modules/events/main.tf"],
        "resources": {
            "aws_cloudwatch_event_rule.managed": "",
            "aws_cloudwatch_event_target.managed": ""
        }
    },
    {
        "json_file": "../sqs.auto.tfvars.json",
        "json_key": "sqs_queues",
        "tf_module": "module.sqs",
        "tf_files": ["../../../modules/sqs/main.tf"],
        "resources": {
            "aws_sqs_queue.managed": "",
            "aws_sqs_queue_policy.managed": ""
        }
    },
    {
        "json_file": "../stepfunctions.auto.tfvars.json",
        "json_key": "state_machines",
        "tf_module": "module.stepfunctions",
        "tf_files": ["../../../modules/stepfunctions/main.tf"],
        "resources": {
            "aws_sfn_state_machine.managed": ""
        }
    },
    {
        "json_file": "../api_gateway.auto.tfvars.json",
        "json_key": "rest_apis",
        "tf_module": "module.apigateway",
        "tf_files": ["../../../modules/apigateway/main.tf"],
        "resources": {
            "aws_api_gateway_rest_api.managed": ""
        }
    },
    {
        "json_file": "../api_gateway.auto.tfvars.json",
        "json_key": "account",
        "tf_module": "module.apigateway",
        "tf_files": ["../../../modules/apigateway/main.tf"],
        "resources": {
            "aws_api_gateway_account.managed": ""
        }
    },
    {
        "json_file": "../api_gateway.auto.tfvars.json",
        "json_key": "domain_names",
        "tf_module": "module.apigateway",
        "tf_files": ["../../../modules/apigateway/main.tf"],
        "resources": {
            "aws_api_gateway_domain_name.managed": ""
        }
    },
    {
        "json_file": "../api_gateway.auto.tfvars.json",
        "json_key": "stages",
        "tf_module": "module.apigateway",
        "tf_files": ["../../../modules/apigateway/main.tf"],
        "resources": {
            "aws_api_gateway_stage.managed": ""
        }
    },
    {
        "json_file": "../api_gateway.auto.tfvars.json",
        "json_key": "resources",
        "tf_module": "module.apigateway",
        "tf_files": ["../../../modules/apigateway/main.tf"],
        "resources": {
            "aws_api_gateway_resource.managed": ""
        }
    },
    {
        "json_file": "../api_gateway.auto.tfvars.json",
        "json_key": "methods",
        "tf_module": "module.apigateway",
        "tf_files": ["../../../modules/apigateway/main.tf"],
        "resources": {
            "aws_api_gateway_method.managed": ""
        }
    },
    {
        "json_file": "../api_gateway.auto.tfvars.json",
        "json_key": "method_responses",
        "tf_module": "module.apigateway",
        "tf_files": ["../../../modules/apigateway/main.tf"],
        "resources": {
            "aws_api_gateway_method_response.managed": ""
        }
    },
    {
        "json_file": "../api_gateway.auto.tfvars.json",
        "json_key": "integrations",
        "tf_module": "module.apigateway",
        "tf_files": ["../../../modules/apigateway/main.tf"],
        "resources": {
            "aws_api_gateway_integration.managed": ""
        }
    },
    {
        "json_file": "../api_gateway.auto.tfvars.json",
        "json_key": "integration_responses",
        "tf_module": "module.apigateway",
        "tf_files": ["../../../modules/apigateway/main.tf"],
        "resources": {
            "aws_api_gateway_integration_response.managed": ""
        }
    },
    {
        "json_file": "../api_gateway.auto.tfvars.json",
        "json_key": "deployments",
        "tf_module": "module.apigateway",
        "tf_files": ["../../../modules/apigateway/main.tf"],
        "resources": {
            "aws_api_gateway_deployment.managed": ""
        }
    },
    {
        "json_file": "../api_gateway.auto.tfvars.json",
        "json_key": "base_path_mappings",
        "tf_module": "module.apigateway",
        "tf_files": ["../../../modules/apigateway/main.tf"],
        "resources": {
            "aws_api_gateway_base_path_mapping.managed": ""
        }
    },
]

OUTPUT_FILE = "../import.sh"
RESOURCE_BLOCK_RE = re.compile(r'resource\s+"([^"]+)"\s+"([^"]+)"')

def parse_tf_resources(tf_file_paths):
    resources = {}
    for tf_file in tf_file_paths:
        if not os.path.isfile(tf_file):
            print(f"⚠️ Skipping missing file: {tf_file}")
            continue
        with open(tf_file, "r") as f:
            content = f.read()
        for match in RESOURCE_BLOCK_RE.finditer(content):
            r_type = match.group(1)
            r_name = match.group(2)
            key = f"{r_type}.{r_name}"
            resources[key] = {"type": r_type, "name": r_name}
    return resources

def load_json_data(json_file, json_key):
    if not os.path.isfile(json_file):
        print(f"⚠️ JSON file not found: {json_file}")
        return {}
    with open(json_file, "r") as f:
        data = json.load(f)
    return data.get(json_key, {})

def build_resource_address(module_prefix, r_type, r_name, instance_key):
    """Build correct Terraform CLI resource address depending on type."""
    
    # For CloudWatch log groups: avoid escaping
    if module_prefix == "module.cloudwatch" and r_type == "aws_cloudwatch_log_group":
        return f'{module_prefix}.{r_type}.{r_name}["{instance_key}"]'
    
    # Default: use escaped quotes (e.g. for JSON-safe or Terraform file safe)
    escaped_key = instance_key.replace('\\', '\\\\').replace('"', '\\"')
    return f'{module_prefix}.{r_type}.{r_name}[\\"{escaped_key}\\"]'


def generate_import_script():
    lines = ["#!/bin/bash", "set -e\n"]

    for mod in modules:
        tf_module = mod["tf_module"]
        tf_files = mod["tf_files"]
        json_file = mod["json_file"]
        json_key = mod["json_key"]
        resources = mod["resources"]

        print(f"🔍 Processing {tf_module}...")

        tf_defined = parse_tf_resources(tf_files)
        json_data = load_json_data(json_file, json_key)

        if not json_data:
            print(f"⚠️ No data found in {json_file} under key '{json_key}'")
            continue

        for res_key, nested_key in resources.items():
            if res_key not in tf_defined:
                print(f"⚠️ Resource {res_key} not defined in TF files of {tf_module}")
                continue

            r_type = tf_defined[res_key]["type"]
            r_name = tf_defined[res_key]["name"]

            # IAM Specific Handling
            if tf_module == "module.iam_roles":
                if r_type == "aws_iam_role":
                    for role_name in json_data:
                        address = build_resource_address(tf_module, r_type, r_name, role_name)
                        quoted_address = f'"{address}"'
                        import_id = role_name
                        lines.append(f'terraform state show {quoted_address} >/dev/null 2>&1 || terraform import {quoted_address} "{import_id}"')

                elif r_type == "aws_iam_role_policy_attachment":
                    for role_name, role_obj in json_data.items():
                        for policy_arn in role_obj.get("attached_managed_policies", []):
                            key = f"{role_name}-{re.sub(r'[:/]', '_', policy_arn)}"
                            address = build_resource_address(tf_module, r_type, r_name, key)
                            quoted_address = f'"{address}"'
                            import_id = policy_arn
                            lines.append(f'terraform state show {quoted_address} >/dev/null 2>&1 || terraform import {quoted_address} "{import_id}"')

                elif r_type == "aws_iam_role_policy":
                    for role_name, role_obj in json_data.items():
                        for policy_name in role_obj.get("inline_policies", {}):
                            key = f"{role_name}-{policy_name}"
                            import_id = f"{role_name}:{policy_name}"
                            address = build_resource_address(tf_module, r_type, r_name, key)
                            quoted_address = f'"{address}"'
                            lines.append(f'terraform state show {quoted_address} >/dev/null 2>&1 || terraform import {quoted_address} "{import_id}"')

                continue  # IAM handled, skip default below

            elif r_type == "aws_sns_topic_subscription":
                for topic_arn, topic_data in json_data.items():
                    subs = topic_data.get("subscriptions", [])
                    for i, sub in enumerate(subs):
                        key = f"{topic_arn}--{i}"
                        # import_id = f"{topic_arn}:{sub['protocol']}:{sub['endpoint']}"
                        import_id = sub["subscription_arn"]
                        address = build_resource_address(tf_module, r_type, r_name, key)
                        quoted_address = f'"{address}"'
                        lines.append(f'terraform state show {quoted_address} >/dev/null 2>&1 || terraform import {quoted_address} "{import_id}"')
                continue
            
                        # Route Table module specific handling
            elif tf_module == "module.route_table":
                if r_type == "aws_route_table":
                    for route_table_id in json_data:
                        address = build_resource_address(tf_module, r_type, r_name, route_table_id)
                        quoted_address = f'"{address}"'
                        import_id = route_table_id
                        lines.append(f'terraform state show {quoted_address} >/dev/null 2>&1 || terraform import {quoted_address} "{import_id}"')

                elif r_type == "aws_route":
                    for route_table_id, route_table in json_data.items():
                        routes = route_table.get("Routes", [])
                        for i, route in enumerate(routes):
                            key = f"{route_table_id}-{i}"
                            address = build_resource_address(tf_module, r_type, r_name, key)
                            quoted_address = f'"{address}"'
                            # Import ID format depends on which ID is used (gateway_id, nat_gateway_id, etc.)
                            # We try to find one:
                            destination = route.get("DestinationCidrBlock")
                            target_id = (
                                route.get("GatewayId")
                                or route.get("NatGatewayId")
                                or route.get("TransitGatewayId")
                                or route.get("EgressOnlyGatewayId")
                                or route.get("NetworkInterfaceId")
                                or route.get("VpcPeeringConnectionId")
                                # or route.get("InstanceId")  # Uncomment if used
                            )

                            if destination:
                                import_id = f"{route_table_id}_{destination}"
                                lines.append(f'terraform state show {quoted_address} >/dev/null 2>&1 || terraform import {quoted_address} "{import_id}"')
                            else:
                                print(f"⚠️ Skipping route import for {key} — missing destination or target")

                elif r_type == "aws_route_table_association":
                    for route_table_id, route_table in json_data.items():
                        associations = route_table.get("Associations", [])
                        for i, assoc in enumerate(associations):

                            if assoc.get("Main", False):
                                print(f"ℹ️ Skipping main route table association for {route_table_id}-{i}")
                                continue  # 🚫 Skip main associations

                            key = f"{route_table_id}-{i}"
                            address = build_resource_address(tf_module, r_type, r_name, key)
                            quoted_address = f'"{address}"'
                            subnet_id = assoc.get("SubnetId")
                            gateway_id = assoc.get("GatewayId")

                            if subnet_id:
                                import_id = f"{subnet_id}/{route_table_id}"
                                lines.append(f'terraform state show {quoted_address} >/dev/null 2>&1 || terraform import {quoted_address} "{import_id}"')
                            elif gateway_id:
                                import_id = f"{gateway_id}/{route_table_id}"
                                lines.append(f'terraform state show {quoted_address} >/dev/null 2>&1 || terraform import {quoted_address} "{import_id}"')
                            
                            else:
                                print(f"⚠️ Skipping association import for {key} — missing subnet_id/gateway_id")
                continue  # Skip default handler for route_table module

            elif tf_module == "module.nacl":
                if r_type == "aws_network_acl":
                    for acl_id, acl in json_data.items():
                        if acl.get("IsDefault"):
                            continue  # Skip default ACLs here, handled above
                        address = build_resource_address(tf_module, r_type, r_name, acl_id)
                        quoted_address = f'"{address}"'
                        lines.append(f'terraform state show {quoted_address} >/dev/null 2>&1 || terraform import {quoted_address} "{acl_id}"')

                elif r_type == "aws_default_network_acl":
                    for acl_id, acl in json_data.items():
                        if not acl.get("IsDefault"):
                            continue  # Only handle default NACLs
                        address = build_resource_address(tf_module, r_type, r_name, acl_id)
                        quoted_address = f'"{address}"'
                        lines.append(f'terraform state show {quoted_address} >/dev/null 2>&1 || terraform import {quoted_address} "{acl_id}"')
                
                elif r_type == "aws_network_acl_rule":
                    for acl_id, acl in json_data.items():
                        if acl.get("IsDefault"):
                            continue  # Skip default ACLs here

                        entries = acl.get("Entries", [])
                        for entry in entries:
                            rule_number = entry.get("RuleNumber")
                            egress = entry.get("Egress")
                            if rule_number is None or egress is None:
                                print(f"⚠️ Skipping malformed entry in ACL {acl_id}")
                                continue
                            key = f"{acl_id}-{str(egress).lower()}-{rule_number}"
                            address = build_resource_address(tf_module, r_type, r_name, key)
                            quoted_address = f'"{address}"'
                            import_id = f"{acl_id}:{rule_number}:{entry['Protocol']}:{str(egress).lower()}"
                            lines.append(f'terraform state show {quoted_address} >/dev/null 2>&1 || terraform import {quoted_address} "{import_id}"')
                continue  # skip default

            elif tf_module == "module.security_groups":
                if r_type == "aws_security_group":
                    # Import the security groups themselves
                    for sg_id, sg_data in json_data.items():
                        # Assuming the security group ID is the key in your JSON data
                        address = build_resource_address(tf_module, r_type, r_name, sg_id)
                        quoted_address = f'"{address}"'
                        import_id = sg_id
                        lines.append(f'terraform state show {quoted_address} >/dev/null 2>&1 || terraform import {quoted_address} "{import_id}"')

                elif r_type == "aws_security_group_rule":
                    # Handle ingress and egress rules separately
                    if nested_key == "IngressRules":
                        for sg_id, sg_data in json_data.items():
                            ingress_rules = sg_data.get("IngressRules", [])
                            for i, rule in enumerate(ingress_rules):
                                key = f"{sg_id}-{i}"
                                address = build_resource_address(tf_module, r_type, r_name, key)
                                quoted_address = f'"{address}"'
                                import_id = f"{sg_id}-{rule['FromPort']}-{rule['ToPort']}-{rule['IpProtocol']}"
                                lines.append(f'terraform state show {quoted_address} >/dev/null 2>&1 || terraform import {quoted_address} "{import_id}"')

                    elif nested_key == "EgressRules":
                        for sg_id, sg_data in json_data.items():
                            egress_rules = sg_data.get("EgressRules", [])
                            for i, rule in enumerate(egress_rules):
                                key = f"{sg_id}-{i}"
                                address = build_resource_address(tf_module, r_type, r_name, key)
                                quoted_address = f'"{address}"'
                                import_id = f"{sg_id}-{rule['FromPort']}-{rule['ToPort']}-{rule['IpProtocol']}"
                                lines.append(f'terraform state show {quoted_address} >/dev/null 2>&1 || terraform import {quoted_address} "{import_id}"')

                continue  # Skip default handler for security groups module

            # NAT Gateway Import Handling
            elif r_type == "aws_nat_gateway":
                for nat_gateway_id, nat_data in json_data.items():
                    # Import the NAT Gateway
                    address = build_resource_address(tf_module, r_type, r_name, nat_gateway_id)
                    quoted_address = f'"{address}"'
                    import_id = nat_gateway_id
                    lines.append(f'terraform state show {quoted_address} >/dev/null 2>&1 || terraform import {quoted_address} "{import_id}"')

            # Specific handling for EIPs
            if r_type == "aws_eip":
                for allocation_id, eip_data in json_data.items():
                    address = build_resource_address(tf_module, r_type, r_name, allocation_id)
                    quoted_address = f'"{address}"'
                    import_id = allocation_id
                    lines.append(f'terraform state show {quoted_address} >/dev/null 2>&1 || terraform import {quoted_address} "{import_id}"')

            elif tf_module == "module.cloudtrail":
                if r_type == "aws_cloudtrail":
                    for trail_name, trail_data in json_data.items():
                        home_region = trail_data.get("home_region", "us-east-1")  # fallback to default region
                        # Extract account ID from one of the ARNs in the JSON, e.g. cloud_watch_logs_role_arn
                        role_arn = trail_data.get("cloud_watch_logs_role_arn", "")
                        account_id_match = re.search(r'arn:aws:iam::(\d+):role/', role_arn)
                        account_id = account_id_match.group(1) if account_id_match else "<account_id>"
                        
                        import_id = f"arn:aws:cloudtrail:{home_region}:{account_id}:trail/{trail_name}"
                        address = build_resource_address(tf_module, r_type, r_name, trail_name)
                        quoted_address = f'"{address}"'
                        lines.append(f'terraform state show {quoted_address} >/dev/null 2>&1 || terraform import {quoted_address} "{import_id}"')
                continue

            elif tf_module == "module.cloudwatch":
                print(f" module.cloudwatch {r_type}")

                if r_type == "aws_cloudwatch_log_group":
                    for log_group_name in json_data:
                        address = build_resource_address(tf_module, r_type, r_name, log_group_name)
                        quoted_address = f"'{address}'"
                        quoted_id = f"'{log_group_name}'"

                        # Use MSYS_NO_PATHCONV=1 to avoid Git Bash path conversion issues
                        lines.append(
                            f"terraform state show {quoted_address} >/dev/null 2>&1 || MSYS_NO_PATHCONV=1 terraform import {quoted_address} {quoted_id}"
                        )
                continue
            
            elif r_type == "aws_cognito_user_pool_client":
                for client_id, client_data in json_data.items():
                    user_pool_id = client_data.get("user_pool_id")
                    if not user_pool_id:
                        print(f"⚠️ Skipping {client_id} — missing user_pool_id")
                        continue
                    
                    address = build_resource_address(tf_module, r_type, r_name, client_id)
                    quoted_address = f'"{address}"'
                    import_id = f"{user_pool_id}/{client_id}"
                    
                    lines.append(f'terraform state show {quoted_address} >/dev/null 2>&1 || terraform import {quoted_address} "{import_id}"')
                continue

            if tf_module == "module.config":
                if r_type == "aws_config_configuration_recorder":
                    for recorder_name in json_data:
                        address = build_resource_address(tf_module, r_type, r_name, recorder_name)
                        quoted_address = f'"{address}"'
                        import_id = recorder_name
                        lines.append(f'terraform state show {quoted_address} >/dev/null 2>&1 || terraform import {quoted_address} "{import_id}"')

                elif r_type == "aws_config_delivery_channel":
                    # Load from separate JSON section if needed
                    if nested_key and ":" in nested_key:
                        json_file_path, json_data_key = nested_key.split(":")
                        delivery_data = load_json_data(json_file_path, json_data_key)
                    else:
                        delivery_data = json_data

                    for channel_name in delivery_data:
                        address = build_resource_address(tf_module, r_type, r_name, channel_name)
                        quoted_address = f'"{address}"'
                        import_id = channel_name
                        lines.append(f'terraform state show {quoted_address} >/dev/null 2>&1 || terraform import {quoted_address} "{import_id}"')

                elif r_type == "aws_config_configuration_recorder_status":
                    for recorder_name in json_data:
                        address = build_resource_address(tf_module, r_type, r_name, recorder_name)
                        quoted_address = f'"{address}"'
                        import_id = recorder_name
                        lines.append(f'terraform state show {quoted_address} >/dev/null 2>&1 || terraform import {quoted_address} "{import_id}"')

                continue  # skip default handling for config

            elif r_type == "aws_kms_alias":
                for key_id, key_data in json_data.items():
                    alias_name = key_data.get("alias_name")
                    if not alias_name:
                        continue  # Skip if alias_name isn't defined

                    address = build_resource_address(tf_module, r_type, r_name, alias_name)
                    quoted_address = f'"{address}"'
                    import_id = alias_name
                    lines.append(f'terraform state show {quoted_address} >/dev/null 2>&1 || terraform import {quoted_address} "{import_id}"')
                continue

            elif r_type == "aws_wafv2_web_acl":
                for arn, cfg in json_data.items():
                    # Extract information from the ARN
                    arn_parts = arn.split("|")  # Split on ':' to isolate the parts of the ARN
                    if len(arn_parts) == 3:

                        name = arn_parts[0]
                        id = arn_parts[1]
                        scope = arn_parts[2]

                        # Build the resource address using the format required by Terraform
                        # address = f"module.waf.aws_wafv2_web_acl.managed['\{name}|{id}|{scope}'\]"
                        waf_name = f"{name}|{id}|{scope}"
                        address = build_resource_address(tf_module, r_type, r_name, waf_name)
                        quoted_address = f'"{address}"'
                        
                        # The correct terraform import statement should be
                        lines.append(f'terraform state show {quoted_address} >/dev/null 2>&1 || terraform import {quoted_address} "{id}/{name}/{scope}"')
                continue  

            elif r_type == "aws_cloudwatch_event_rule":
                for rule_name, rule_data in json_data.items():
                    address = build_resource_address(tf_module, r_type, r_name, rule_name)
                    quoted_address = f'"{address}"'
                    lines.append(f'terraform state show {quoted_address} >/dev/null 2>&1 || terraform import {quoted_address} "{rule_name}"')
                continue

            elif r_type == "aws_cloudwatch_event_target":
                for rule_name, rule_data in json_data.items():
                    if rule_data.get("targets"):
                        target_id = rule_data["targets"].get("target_id", "default")
                        # The resource key is the rule name (each.key in the for_each)
                        address = build_resource_address(tf_module, r_type, r_name, rule_name)
                        quoted_address = f'"{address}"'
                        # Import format: rule_name/target_id
                        lines.append(f'terraform state show {quoted_address} >/dev/null 2>&1 || terraform import {quoted_address} "{rule_name}/{target_id}"')
                continue

            elif r_type == "aws_sqs_queue":
                for queue_name, queue_data in json_data.items():
                    address = build_resource_address(tf_module, r_type, r_name, queue_name)
                    quoted_address = f'"{address}"'
                    lines.append(f'terraform state show {quoted_address} >/dev/null 2>&1 || terraform import {quoted_address} "{queue_name}"')
                continue

            elif r_type == "aws_sqs_queue_policy":
                for queue_name, queue_data in json_data.items():
                    if queue_data.get("policy"):
                        address = build_resource_address(tf_module, r_type, r_name, queue_name)
                        quoted_address = f'"{address}"'
                        lines.append(f'terraform state show {quoted_address} >/dev/null 2>&1 || terraform import {quoted_address} "{queue_name}"')
                continue

            elif r_type == "aws_sfn_state_machine":
                for sm_arn, sm_data in json_data.items():
                    # Use ARN as instance key
                    address = build_resource_address(tf_module, r_type, r_name, sm_arn)
                    quoted_address = f'"{address}"'
                    import_id = sm_arn
                    lines.append(f'terraform state show {quoted_address} >/dev/null 2>&1 || terraform import {quoted_address} "{import_id}"')
                continue

            # API Gateway specific handling
            if tf_module == "module.apigateway":
                if r_type == "aws_api_gateway_rest_api":
                    # json_data is keyed by CFN rid; each value contains the real RestApi id under 'id'
                    for rid, api_obj in json_data.items():
                        api_id = api_obj.get("id") or rid
                        address = build_resource_address(tf_module, r_type, r_name, rid)
                        quoted_address = f'"{address}"'
                        import_id = api_id
                        lines.append(f'terraform state show {quoted_address} >/dev/null 2>&1 || terraform import {quoted_address} "{import_id}"')
                    continue

                elif r_type == "aws_api_gateway_account":
                    # json_data keyed by CFN rid; import id is literal 'api-gateway-account'
                    for rid in json_data.keys():
                        address = build_resource_address(tf_module, r_type, r_name, rid)
                        quoted_address = f'"{address}"'
                        lines.append(f'terraform state show {quoted_address} >/dev/null 2>&1 || terraform import {quoted_address} "api-gateway-account"')
                    continue

                elif r_type == "aws_api_gateway_domain_name":
                    # json_data keyed by CFN rid, which equals the domain name
                    for domain_name in json_data.keys():
                        address = build_resource_address(tf_module, r_type, r_name, domain_name)
                        quoted_address = f'"{address}"'
                        import_id = domain_name
                        lines.append(f'terraform state show {quoted_address} >/dev/null 2>&1 || terraform import {quoted_address} "{import_id}"')
                    continue

                elif r_type == "aws_api_gateway_stage":
                    # json_data keyed by CFN rid. Each value has rest_api_id and stage_name
                    for rid, stage_obj in json_data.items():
                        api_id = stage_obj.get("rest_api_id")
                        stage_name = stage_obj.get("stage_name")
                        # Use the original rid as the key (not api_id|stage_name)
                        address = build_resource_address(tf_module, r_type, r_name, rid)
                        quoted_address = f'"{address}"'
                        import_id = f"{api_id}/{stage_name}" if api_id and stage_name else stage_name or rid
                        lines.append(f'terraform state show {quoted_address} >/dev/null 2>&1 || terraform import {quoted_address} "{import_id}"')
                    continue

                elif r_type == "aws_api_gateway_resource":
                    # json_data keyed by resource id; value contains rest_api_id and id
                    for resource_id, resource_obj in json_data.items():
                        api_id = resource_obj.get("rest_api_id")
                        rid = resource_obj.get("id", resource_id)
                        address = build_resource_address(tf_module, r_type, r_name, resource_id)
                        quoted_address = f'"{address}"'
                        import_id = f"{api_id}/{rid}"
                        lines.append(f'terraform state show {quoted_address} >/dev/null 2>&1 || terraform import {quoted_address} "{import_id}"')
                    continue

                elif r_type == "aws_api_gateway_method":
                    # json_data keyed by resourceId|httpMethod
                    for method_key, method_obj in json_data.items():
                        api_id = method_obj.get("rest_api_id")
                        resource_id = method_obj.get("resource_id")
                        http_method = method_obj.get("http_method")
                        address = build_resource_address(tf_module, r_type, r_name, method_key)
                        quoted_address = f'"{address}"'
                        import_id = f"{api_id}/{resource_id}/{http_method}"
                        lines.append(f'terraform state show {quoted_address} >/dev/null 2>&1 || terraform import {quoted_address} "{import_id}"')
                    continue

                elif r_type == "aws_api_gateway_method_response":
                    # json_data keyed by resourceId|httpMethod|statusCode
                    for resp_key, resp_obj in json_data.items():
                        api_id = resp_obj.get("rest_api_id")
                        resource_id = resp_obj.get("resource_id")
                        http_method = resp_obj.get("http_method")
                        status_code = resp_obj.get("status_code")
                        address = build_resource_address(tf_module, r_type, r_name, resp_key)
                        quoted_address = f'"{address}"'
                        import_id = f"{api_id}/{resource_id}/{http_method}/{status_code}"
                        lines.append(f'terraform state show {quoted_address} >/dev/null 2>&1 || terraform import {quoted_address} "{import_id}"')
                    continue

                elif r_type == "aws_api_gateway_integration":
                    # json_data keyed by resourceId|httpMethod
                    for int_key, int_obj in json_data.items():
                        api_id = int_obj.get("rest_api_id")
                        resource_id = int_obj.get("resource_id")
                        http_method = int_obj.get("http_method")
                        address = build_resource_address(tf_module, r_type, r_name, int_key)
                        quoted_address = f'"{address}"'
                        import_id = f"{api_id}/{resource_id}/{http_method}"
                        lines.append(f'terraform state show {quoted_address} >/dev/null 2>&1 || terraform import {quoted_address} "{import_id}"')
                    continue

                elif r_type == "aws_api_gateway_integration_response":
                    # json_data keyed by resourceId|httpMethod|statusCode
                    for int_resp_key, int_resp_obj in json_data.items():
                        api_id = int_resp_obj.get("rest_api_id")
                        resource_id = int_resp_obj.get("resource_id")
                        http_method = int_resp_obj.get("http_method")
                        status_code = int_resp_obj.get("status_code")
                        address = build_resource_address(tf_module, r_type, r_name, int_resp_key)
                        quoted_address = f'"{address}"'
                        import_id = f"{api_id}/{resource_id}/{http_method}/{status_code}"
                        lines.append(f'terraform state show {quoted_address} >/dev/null 2>&1 || terraform import {quoted_address} "{import_id}"')
                    continue

                elif r_type == "aws_api_gateway_deployment":
                    # json_data keyed by deployment id
                    for deployment_id, deployment_obj in json_data.items():
                        api_id = deployment_obj.get("rest_api_id")
                        address = build_resource_address(tf_module, r_type, r_name, deployment_id)
                        quoted_address = f'"{address}"'
                        import_id = f"{api_id}/{deployment_id}"
                        lines.append(f'terraform state show {quoted_address} >/dev/null 2>&1 || terraform import {quoted_address} "{import_id}"')
                    continue

                elif r_type == "aws_api_gateway_base_path_mapping":
                    # json_data keyed by domain|basePath
                    for mapping_key, mapping_obj in json_data.items():
                        domain_name = mapping_obj.get("domain_name")
                        base_path = mapping_obj.get("base_path", "")
                        address = build_resource_address(tf_module, r_type, r_name, mapping_key)
                        quoted_address = f'"{address}"'
                        # Import ID: domain_name/base_path (empty string if no base path)
                        import_id = f"{domain_name}/{base_path}"
                        lines.append(f'terraform state show {quoted_address} >/dev/null 2>&1 || terraform import {quoted_address} "{import_id}"')
                    continue

            # General (non-nested) handling
            target_data = json_data.get(nested_key, {}) if nested_key else json_data
            for instance_key in target_data:
                address = build_resource_address(tf_module, r_type, r_name, instance_key)
                quoted_address = f'"{address}"'
                import_cmd = f'terraform import {quoted_address} "{instance_key}"'
                check_cmd = f'terraform state show {quoted_address} >/dev/null 2>&1'
                lines.append(f'{check_cmd} || {import_cmd}')

    with open(OUTPUT_FILE, "w") as f:
        f.write("\n".join(lines))

    os.chmod(OUTPUT_FILE, os.stat(OUTPUT_FILE).st_mode | stat.S_IEXEC)
    print(f"✅ Import script generated → {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_import_script()
