import os
import boto3
import json
import requests
from botocore.exceptions import ClientError


cf = boto3.client("cloudformation")
s3 = boto3.client("s3")
dynamodb = boto3.client("dynamodb")
lambda_client = boto3.client("lambda")
iam = boto3.client("iam")

# -----------------------
# Function: List all stacks
# -----------------------
def list_stacks():
    stacks = []
    paginator = cf.get_paginator("list_stacks")
    for page in paginator.paginate(StackStatusFilter=["CREATE_COMPLETE", "UPDATE_COMPLETE"]):
        for stack in page["StackSummaries"]:
            stacks.append(stack["StackName"])
    return stacks

# -----------------------
# Function: List stack resources
# -----------------------
def list_stack_resources(stack_name):
    resources = []
    paginator = cf.get_paginator("list_stack_resources")
    for page in paginator.paginate(StackName=stack_name):
        resources.extend(page["StackResourceSummaries"])
    return resources

# -----------------------
# Function: Get S3 bucket config
# -----------------------
def get_s3_config(bucket_name):
    try:
        # Region
        region = s3.get_bucket_location(Bucket=bucket_name)["LocationConstraint"]
        if region is None:  # us-east-1 special case
            region = "us-east-1"

        # Creation date
        creation_date = None
        for b in s3.list_buckets()["Buckets"]:
            if b["Name"] == bucket_name:
                creation_date = b["CreationDate"].isoformat()
                break

        # Versioning
        versioning = s3.get_bucket_versioning(Bucket=bucket_name)
        versioning_status = versioning.get("Status", "Disabled")

        return {
            "bucket": bucket_name,
            "region": region,
            "creation_date": creation_date,
            "versioning_status": versioning_status,
        }
    except Exception as e:
        print(f"⚠️ Error fetching bucket {bucket_name}: {e}")
        return None

# -----------------------
# Function: Get DynamoDB table config
# -----------------------
def get_dynamodb_config(table_name):
    try:
        desc = dynamodb.describe_table(TableName=table_name)["Table"]
        return {
            "table_name": desc["TableName"],
            "region": dynamodb.meta.region_name,
            "status": desc["TableStatus"],
            "billing_mode": desc.get("BillingModeSummary", {}).get("BillingMode", "PROVISIONED"),
            "read_capacity": desc.get("ProvisionedThroughput", {}).get("ReadCapacityUnits"),
            "write_capacity": desc.get("ProvisionedThroughput", {}).get("WriteCapacityUnits"),
            "key_schema": desc["KeySchema"],
            "attributes": desc["AttributeDefinitions"],
        }
    except Exception as e:
        print(f"⚠️ Error fetching DynamoDB table {table_name}: {e}")
        return None

# -----------------------
# Function: Get Lambda config
# -----------------------

def get_lambda_config(function_name):
    try:
        response = lambda_client.get_function(FunctionName=function_name)
        func = response["Configuration"]
        code = response.get("Code", {})

        # Get VPC config
        vpc_config = func.get("VpcConfig", {})
        vpc_info = {
            "subnet_ids": vpc_config.get("SubnetIds", []),
            "security_group_ids": vpc_config.get("SecurityGroupIds", []),
            "vpc_id": vpc_config.get("VpcId", None),
        }

        # Get DLQ
        dlq_target = func.get("DeadLetterConfig", {}).get("TargetArn")

        # Tracing
        tracing_mode = func.get("TracingConfig", {}).get("Mode", "PassThrough")

        # Layers
        layers = [layer["Arn"] for layer in func.get("Layers", [])]

        # Fetch aliases
        aliases_response = lambda_client.list_aliases(FunctionName=function_name)
        aliases = [
            {
                "name": alias["Name"],
                "description": alias.get("Description", ""),
                "function_version": alias.get("FunctionVersion")
            }
            for alias in aliases_response.get("Aliases", [])
        ]

        # Download code if Zip type
        local_code_path = None
        if func.get("PackageType") == "Zip" and "Location" in code:
            os.makedirs("code", exist_ok=True)
            local_code_path = f"code/{function_name}.zip"
            try:
                print('')
                # download_lambda_code(code["Location"], local_code_path)
            except Exception as e:
                print(f"⚠️ Failed to download Lambda code: {e}")
                local_code_path = None

        return {
            "function_name": func["FunctionName"],
            "runtime": func.get("Runtime"),
            "handler": func.get("Handler"),
            "role": func.get("Role"),
            "description": func.get("Description", ""),
            "memory_size": func.get("MemorySize"),
            "timeout": func.get("Timeout"),
            "last_modified": func.get("LastModified"),
            "region": lambda_client.meta.region_name,
            "environment": func.get("Environment", {}).get("Variables", {}),
            "architectures": func.get("Architectures", []),
            "ephemeral_storage": func.get("EphemeralStorage", {}).get("Size", 512),
            "kms_key_arn": func.get("KMSKeyArn"),
            "layers": layers,
            "vpc_config": vpc_info,
            "dead_letter_queue": dlq_target,
            "tracing_mode": tracing_mode,
            "package_type": func.get("PackageType", "Zip"),
            "image_config": func.get("ImageConfigResponse", {}),
            "code_sha256": func.get("CodeSha256"),
            "code_size": func.get("CodeSize"),
            "publish_version": True if func.get("Version") != "$LATEST" else False,
            "version": func.get("Version"),
            "aliases": aliases,
            "dummy_filename": local_code_path
        }

    except Exception as e:
        print(f"⚠️ Error fetching Lambda {function_name}: {e}")
        return None

# -----------------------
# Function: Download Lambda code
# -----------------------
def download_lambda_code(url, filename):
    """Download the Lambda deployment package to a local file"""
    response = requests.get(url)
    response.raise_for_status()
    with open(filename, "wb") as f:
        f.write(response.content)

# -----------------------
# Normalize IAM tags
# -----------------------
def normalize_tags(tags):
    """
    Accepts AWS tag list or dict and normalizes into list of {key,value} objects.
    """
    if isinstance(tags, list):
        # Already a list of {"Key":..., "Value":...}
        return [{"key": t["Key"], "value": t["Value"]} for t in tags]
    elif isinstance(tags, dict):
        # Convert dict {"k":"v"} -> [{"key":"k","value":"v"}]
        return [{"key": k, "value": v} for k, v in tags.items()]
    else:
        return []

def ensure_policy_version(policy_doc):
    # Make sure 'Version' exists, else set default AWS policy version
    if not policy_doc.get("Version"):
        policy_doc["Version"] = "2012-10-17"
    return policy_doc


# -----------------------
# Normalize inline policies
# -----------------------
def normalize_inline_policies(role_name):
    inline = {}
    inline_paginator = iam.get_paginator("list_role_policies")
    for page in inline_paginator.paginate(RoleName=role_name):
        for pname in page.get("PolicyNames", []):
            pol_doc = iam.get_role_policy(
                RoleName=role_name,
                PolicyName=pname
            )["PolicyDocument"]
            pol_doc = normalize_policy_doc(pol_doc)
            pol_doc = ensure_policy_version(pol_doc)   # <-- Add this line
            inline[pname] = pol_doc
    return inline

# -----------------------
# Normalize Inline Policy
# -----------------------
def normalize_policy_doc(policy_doc):
    """
    Ensures inline policy is always a dict.
    Handles cases where AWS SDK returns already parsed dict or a JSON string.
    """
    if isinstance(policy_doc, str):
        try:
            return json.loads(policy_doc)
        except json.JSONDecodeError:
            return {}  # fallback, shouldn't happen normally
    return policy_doc


def fill_missing_role_fields(role):
    # Defaults
    role.setdefault("path", "/")
    role.setdefault("description", "")
    role.setdefault("max_session_duration", 3600)
    role.setdefault("permissions_boundary", "")
    role.setdefault("tags", [])
    role.setdefault("attached_managed_policies", [])
    role.setdefault("inline_policies", {})
    return role

# -----------------------
# Get IAM Role config
# -----------------------
def get_iam_role_config(role_name):
    try:
        resp = iam.get_role(RoleName=role_name)
        role = resp["Role"]

        # Tags
        tags_resp = iam.list_role_tags(RoleName=role_name)
        tags = normalize_tags(tags_resp.get("Tags", []))

        # Managed policies
        attached = []
        paginator = iam.get_paginator("list_attached_role_policies")
        for page in paginator.paginate(RoleName=role_name):
            for ap in page.get("AttachedPolicies", []):
                attached.append(ap["PolicyArn"])

        # Inline policies (normalized)
        inline = normalize_inline_policies(role_name)

        return {
            "role_name": role["RoleName"],
            "arn": role["Arn"],
            "path": role.get("Path"),
            "assume_role_policy": role.get("AssumeRolePolicyDocument"),
            "description": role.get("Description"),
            "max_session_duration": role.get("MaxSessionDuration"),
            "permissions_boundary": role.get("PermissionsBoundary", {}).get("PermissionsBoundaryArn"),
            "tags": tags,
            "attached_managed_policies": attached,
            "inline_policies": inline
        }
    except ClientError as e:
        print(f"⚠️ Error fetching IAM Role {role_name}: {e}")
        return None

# -----------------------
# Get IAM User config
# -----------------------
def get_iam_user_config(user_name):
    try:
        resp = iam.get_user(UserName=user_name)
        user = resp["User"]
        tags_resp = iam.list_user_tags(UserName=user_name)
        tags = tags_resp.get("Tags", [])

        attached = []
        pag = iam.get_paginator("list_attached_user_policies")
        for page in pag.paginate(UserName=user_name):
            for ap in page.get("AttachedPolicies", []):
                attached.append(ap["PolicyArn"])

        inline = {}
        inline_p = iam.get_paginator("list_user_policies")
        for page in inline_p.paginate(UserName=user_name):
            for pname in page.get("PolicyNames", []):
                pol_doc = iam.get_user_policy(UserName=user_name, PolicyName=pname)["PolicyDocument"]
                # Store as JSON string (consistent with roles)
                # inline[pname] = json.dumps(pol_doc, separators=(",", ":"))
                inline[pname] = normalize_policy_doc(pol_doc)  # instead of json.dumps

        return {
            "user_name": user["UserName"],
            "arn": user["Arn"],
            "path": user.get("Path"),
            "create_date": user.get("CreateDate").isoformat() if "CreateDate" in user else None,
            "tags": tags,
            "attached_managed_policies": attached,
            "inline_policies": inline
        }
    except ClientError as e:
        print(f"⚠️ Error fetching IAM User {user_name}: {e}")
        return None

# -----------------------
# Get IAM Group config
# -----------------------
def get_iam_group_config(group_name):
    try:
        resp = iam.get_group(GroupName=group_name)
        group = resp["Group"]
        tags_resp = iam.list_group_tags(GroupName=group_name)
        tags = tags_resp.get("Tags", [])

        members = [u["UserName"] for u in resp.get("Users", [])]

        attached = []
        pag = iam.get_paginator("list_attached_group_policies")
        for page in pag.paginate(GroupName=group_name):
            for ap in page.get("AttachedPolicies", []):
                attached.append(ap["PolicyArn"])

        inline = {}
        inline_p = iam.get_paginator("list_group_policies")
        for page in inline_p.paginate(GroupName=group_name):
            for pname in page.get("PolicyNames", []):
                pol_doc = iam.get_group_policy(GroupName=group_name, PolicyName=pname)["PolicyDocument"]
                inline[pname] = normalize_policy_doc(pol_doc)  # instead of json.dumps

        return {
            "group_name": group["GroupName"],
            "arn": group["Arn"],
            "path": group.get("Path"),
            "create_date": group.get("CreateDate").isoformat(),
            "tags": tags,
            "members": members,
            "attached_managed_policies": attached,
            "inline_policies": inline
        }
    except ClientError as e:
        print(f"⚠️ Error fetching IAM Group {group_name}: {e}")
        return None

# -----------------------
# Get IAM Policy (Managed)
# -----------------------
def get_iam_managed_policy_config(policy_arn):
    try:
        resp = iam.get_policy(PolicyArn=policy_arn)
        policy = resp["Policy"]
        # Default version
        default_ver_id = policy["DefaultVersionId"]
        ver_resp = iam.get_policy_version(PolicyArn=policy_arn, VersionId=default_ver_id)
        policy_doc = ver_resp["PolicyVersion"]["Document"]

        tags_resp = iam.list_policy_tags(PolicyArn=policy_arn)
        tags = tags_resp.get("Tags", [])

        # Entities this policy is attached to:
        entities = iam.list_entities_for_policy(PolicyArn=policy_arn)
        # entities gives Users, Groups, Roles

        return {
            "policy_name": policy["PolicyName"],
            "arn": policy["Arn"],
            "path": policy.get("Path"),
            "default_version_id": default_ver_id,
            "policy_document": policy_doc,
            "tags": tags,
            "attached_entities": {
                "users": [u["UserName"] for u in entities.get("PolicyUsers", [])],
                "roles": [r["RoleName"] for r in entities.get("PolicyRoles", [])],
                "groups": [g["GroupName"] for g in entities.get("PolicyGroups", [])],
            }
        }
    except ClientError as e:
        print(f"⚠️ Error fetching IAM Policy {policy_arn}: {e}")
        return None

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

    stacks = list_stacks()
    print(f"📦 Found {len(stacks)} stacks")

    for stack in stacks:
        print(f"\n🔍 Processing stack: {stack}")
        resources = list_stack_resources(stack)

        for res in resources:
            rtype = res["ResourceType"]
            rid = res["PhysicalResourceId"]

            if rtype == "AWS::S3::Bucket":
                print(f"   → Found bucket: {rid}")
                bucket_config = get_s3_config(rid)
                if bucket_config:
                    all_buckets[rid] = bucket_config

            elif rtype == "AWS::DynamoDB::Table":
                print(f"   → Found DynamoDB table: {rid}")
                table_config = get_dynamodb_config(rid)
                if table_config:
                    all_dynamodb[rid] = table_config

            elif rtype == "AWS::Lambda::Function":
                print(f"   → Found Lambda function: {rid}")
                lambda_config = get_lambda_config(rid)
                if lambda_config:
                    all_lambdas[rid] = lambda_config

            elif rtype == "AWS::IAM::Role":
                print(f"   → Found IAM Role: {rid}")
                role_config = get_iam_role_config(rid)
                if role_config:
                    role_config = fill_missing_role_fields(role_config)
                    all_roles[rid] = role_config

            elif rtype == "AWS::IAM::User":
                print(f"   → Found IAM User: {rid}")
                user_config = get_iam_user_config(rid)
                if user_config:
                    all_users[rid] = user_config

            elif rtype == "AWS::IAM::Group":
                print(f"   → Found IAM Group: {rid}")
                group_config = get_iam_group_config(rid)
                if group_config:
                    all_groups[rid] = group_config

            elif rtype == "AWS::IAM::Policy":
                print(f"   → Found IAM Policy: {rid}")
                policy_config = get_iam_managed_policy_config(rid)
                if policy_config:
                    all_managed_policies[rid] = policy_config

    # Save outputs
    if all_buckets:
        with open("s3.auto.tfvars.json", "w") as f:
            json.dump({"buckets": all_buckets}, f, indent=2)
        print("✅ Exported S3 buckets → s3.auto.tfvars.json")

    if all_dynamodb:
        with open("dynamodb.auto.tfvars.json", "w") as f:
            json.dump({"dynamodb_tables": all_dynamodb}, f, indent=2)
        print("✅ Exported DynamoDB tables → dynamodb.auto.tfvars.json")

    if all_lambdas:
        with open("lambda.auto.tfvars.json", "w") as f:
            json.dump({"functions": all_lambdas}, f, indent=2)
        print("✅ Exported Lambdas → lambda.auto.tfvars.json")

    if all_roles:
        with open("iam_roles.auto.tfvars.json", "w") as f:
            json.dump({"roles": all_roles}, f, indent=2)
        print("✅ Exported IAM Roles → iam_roles.auto.tfvars.json")

    if all_users:
        with open("iam_users.auto.tfvars.json", "w") as f:
            json.dump({"users": all_users}, f, indent=2)
        print("✅ Exported IAM Users → iam_users.auto.tfvars.json")

    if all_groups:
        with open("iam_groups.auto.tfvars.json", "w") as f:
            json.dump({"groups": all_groups}, f, indent=2)
        print("✅ Exported IAM Groups → iam_groups.auto.tfvars.json")

    if all_managed_policies:
        with open("iam_policies.auto.tfvars.json", "w") as f:
            json.dump({"policies": all_managed_policies}, f, indent=2)
        print("✅ Exported IAM Managed Policies → iam_policies.auto.tfvars.json")


if __name__ == "__main__":
    main()
