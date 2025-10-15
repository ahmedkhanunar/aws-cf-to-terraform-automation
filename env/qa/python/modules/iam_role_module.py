import boto3
import json
from botocore.exceptions import ClientError

# Initialize the IAM client
iam = boto3.client("iam")

def get_iam_role_config(role_name, role_key=None):
    """
    Fetch the IAM role configuration in Terraform-ready shape for modules/iam.
    Returns a tuple: (role_config, inline_policies_map)
    
    role_config: dict for the role itself
    inline_policies_map: dict keyed by "role_id|policy_name" for inline policies
    """
    try:
        # Base role details
        role_response = iam.get_role(RoleName=role_name)
        role = role_response["Role"]

        # Use provided role_key or sanitize role_name as the key
        if not role_key:
            role_key = role_name.replace("-", "_").replace(".", "_")

        # Permissions boundary ARN (if any)
        permissions_boundary_arn = None
        if role.get("PermissionsBoundary"):
            permissions_boundary_arn = role["PermissionsBoundary"].get("PermissionsBoundaryArn")

        # Collect attached managed policy ARNs with pagination
        attached_policy_arns = []
        paginator = iam.get_paginator("list_attached_role_policies")
        for page in paginator.paginate(RoleName=role_name):
            for policy in page.get("AttachedPolicies", []):
                attached_policy_arns.append(policy["PolicyArn"])

        # Collect inline policies separately
        inline_policies_map = {}
        list_inline_policies_paginator = iam.get_paginator("list_role_policies")
        for page in list_inline_policies_paginator.paginate(RoleName=role_name):
            for policy_name in page.get("PolicyNames", []):
                inline_resp = iam.get_role_policy(RoleName=role_name, PolicyName=policy_name)
                doc = inline_resp.get("PolicyDocument", {})
                
                # Normalize and convert to JSON string for consistent Terraform typing
                normalized_doc = normalize_policy_document(doc)
                policy_json = json.dumps(normalized_doc, sort_keys=True)
                
                # Key format: role_id|policy_name
                policy_key = f"{role_key}|{policy_name}"
                inline_policies_map[policy_key] = {
                    "role_id": role_key,
                    "policy_name": policy_name,
                    "policy_json": policy_json
                }

        # Convert AWS tag list to map(string)
        tags_map = tags_list_to_map(role.get("Tags", []))

        # Normalize assume role policy to JSON string
        assume_role_policy_json = json.dumps(
            normalize_policy_document(role["AssumeRolePolicyDocument"]), 
            sort_keys=True
        )

        # Shape for Terraform module input (role only, no inline policies)
        tf_role = {
            "role_name": role["RoleName"],
            "path": role.get("Path", "/"),
            "assume_role_policy": assume_role_policy_json,
            "description": role.get("Description", ""),
            "max_session_duration": role.get("MaxSessionDuration", 3600),
            "tags": tags_map,
            "attached_managed_policies": attached_policy_arns,
        }

        if permissions_boundary_arn:
            tf_role["permissions_boundary"] = permissions_boundary_arn

        return (tf_role, inline_policies_map)
    except ClientError as e:
        print(f"⚠️ Failed to get IAM role {role_name}: {e}")
        return (None, {})

def get_iam_user_config(user_name):
    """Fetch the IAM user configuration."""
    try:
        # Get user details
        user_response = iam.get_user(UserName=user_name)
        user = user_response["User"]

        # Extract user information
        user_config = {
            "user_name": user["UserName"],
            "user_id": user["UserId"],
            "arn": user["Arn"],
            "create_date": user["CreateDate"].isoformat(),
            "tags": format_tags(user.get("Tags", [])),
        }

        # Get attached policies for the user
        attached_policies = iam.list_attached_user_policies(UserName=user_name)["AttachedPolicies"]
        user_config["attached_policies"] = [
            {"policy_name": policy["PolicyName"], "policy_arn": policy["PolicyArn"]} for policy in attached_policies
        ]

        return user_config
    except ClientError as e:
        print(f"⚠️ Failed to get IAM user {user_name}: {e}")
        return None

def get_iam_group_config(group_name):
    """Fetch the IAM group configuration."""
    try:
        # Get group details
        group_response = iam.get_group(GroupName=group_name)
        group = group_response["Group"]

        # Extract group information
        group_config = {
            "group_name": group["GroupName"],
            "group_id": group["GroupId"],
            "arn": group["Arn"],
            "create_date": group["CreateDate"].isoformat(),
            "tags": format_tags(group.get("Tags", [])),
        }

        # Get attached policies for the group
        attached_policies = iam.list_attached_group_policies(GroupName=group_name)["AttachedPolicies"]
        group_config["attached_policies"] = [
            {"policy_name": policy["PolicyName"], "policy_arn": policy["PolicyArn"]} for policy in attached_policies
        ]

        return group_config
    except ClientError as e:
        print(f"⚠️ Failed to get IAM group {group_name}: {e}")
        return None

def get_iam_managed_policy_config(policy_arn):
    """Fetch the IAM managed policy configuration."""
    try:
        # Get policy details
        policy_response = iam.get_policy(PolicyArn=policy_arn)
        policy = policy_response["Policy"]

        # Extract policy information
        policy_config = {
            "policy_name": policy["PolicyName"],
            "policy_id": policy["PolicyId"],
            "arn": policy["Arn"],
            "default_version_id": policy["DefaultVersionId"],
            "attachment_count": policy["AttachmentCount"],
            "create_date": policy["CreateDate"].isoformat(),
            "tags": format_tags(policy.get("Tags", [])),
        }

        # Get the policy's versions
        versions = iam.list_policy_versions(PolicyArn=policy_arn)["Versions"]
        policy_config["versions"] = [
            {"version_id": version["VersionId"], "is_default_version": version["IsDefaultVersion"]} for version in versions
        ]

        return policy_config
    except ClientError as e:
        print(f"⚠️ Failed to get IAM policy {policy_arn}: {e}")
        return None

def format_tags(tag_list):
    """Convert AWS tag list to Terraform-style list of maps."""
    return [{"Key": tag["Key"], "Value": tag["Value"]} for tag in tag_list]

def tags_list_to_map(tag_list):
    """Convert AWS tag list to a simple map(string) for Terraform variables."""
    return {tag["Key"]: tag["Value"] for tag in tag_list or []}

def normalize_policy_document(doc):
    """
    Normalize an IAM policy document to ensure consistent typing for Terraform.
    Ensures Statement is always a list and all fields are properly typed.
    """
    if not doc:
        return {
            "Version": "2012-10-17",
            "Statement": []
        }
    
    normalized = {
        "Version": doc.get("Version", "2012-10-17"),
    }
    
    # Ensure Statement is always a list
    statement = doc.get("Statement", [])
    if isinstance(statement, dict):
        statement = [statement]
    elif not isinstance(statement, list):
        statement = []
    
    # Normalize each statement
    normalized_statements = []
    for stmt in statement:
        if isinstance(stmt, dict):
            # Ensure all statement fields are consistently typed
            normalized_stmt = {}
            for key, value in stmt.items():
                normalized_stmt[key] = value
            normalized_statements.append(normalized_stmt)
    
    normalized["Statement"] = normalized_statements
    
    # Include any other top-level keys (like Id)
    for key in doc:
        if key not in ["Version", "Statement"]:
            normalized[key] = doc[key]
    
    return normalized

