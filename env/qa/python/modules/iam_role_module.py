import boto3
from botocore.exceptions import ClientError

# Initialize the IAM client
iam = boto3.client("iam")

def get_iam_role_config(role_name):
    """Fetch the IAM role configuration."""
    try:
        # Get role details
        role_response = iam.get_role(RoleName=role_name)
        role = role_response["Role"]

        # Extract the role information
        role_config = {
            "role_name": role["RoleName"],
            "role_id": role["RoleId"],
            "arn": role["Arn"],
            "description": role.get("Description", ""),
            "assume_role_policy_document": role["AssumeRolePolicyDocument"],
            "tags": format_tags(role.get("Tags", [])),
        }

        # Get attached policies for the role
        attached_policies = iam.list_attached_role_policies(RoleName=role_name)["AttachedPolicies"]
        role_config["attached_policies"] = [
            {"policy_name": policy["PolicyName"], "policy_arn": policy["PolicyArn"]} for policy in attached_policies
        ]

        return role_config
    except ClientError as e:
        print(f"⚠️ Failed to get IAM role {role_name}: {e}")
        return None

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

