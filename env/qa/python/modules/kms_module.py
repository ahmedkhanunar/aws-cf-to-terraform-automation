import boto3
from botocore.exceptions import ClientError
import json

kms = boto3.client("kms")

# -----------------------
# Function: Get KMS key config
# -----------------------
def get_kms_key_config(key_id):
    try:
        # Get key metadata
        key_desc = kms.describe_key(KeyId=key_id)
        key_metadata = key_desc["KeyMetadata"]
        
        # Get key policy
        try:
            policy_response = kms.get_key_policy(KeyId=key_id, PolicyName="default")
            policy = policy_response["Policy"]
        except ClientError as e:
            print(f"⚠️ Warning: Could not retrieve policy for key {key_id}: {e}")
            policy = None
        
        # Get key rotation status
        try:
            rotation_response = kms.get_key_rotation_status(KeyId=key_id)
            key_rotation_enabled = rotation_response["KeyRotationEnabled"]
        except ClientError as e:
            print(f"⚠️ Warning: Could not retrieve rotation status for key {key_id}: {e}")
            key_rotation_enabled = False
        
        # Get aliases for this key
        aliases = []
        try:
            aliases_response = kms.list_aliases(KeyId=key_id)
            aliases = [alias["AliasName"] for alias in aliases_response.get("Aliases", [])]
        except ClientError as e:
            print(f"⚠️ Warning: Could not retrieve aliases for key {key_id}: {e}")
        
        # Get tags
        tags = {}
        try:
            tags_response = kms.list_resource_tags(KeyId=key_id)
            tags = {tag["TagKey"]: tag["TagValue"] for tag in tags_response.get("Tags", [])}
        except ClientError as e:
            print(f"⚠️ Warning: Could not retrieve tags for key {key_id}: {e}")

        return {
            "key_id": key_metadata["KeyId"],
            "arn": key_metadata["Arn"],
            "description": key_metadata.get("Description", ""),
            "key_usage": key_metadata.get("KeyUsage", "ENCRYPT_DECRYPT"),
            "customer_master_key_spec": key_metadata.get("CustomerMasterKeySpec", "SYMMETRIC_DEFAULT"),
            "key_rotation_enabled": key_rotation_enabled,
            "deletion_window_in_days": key_metadata.get("DeletionDate"),  # This will be None if not scheduled for deletion
            "policy": policy,
            "alias_name": aliases[0] if aliases else None,  # Take the first alias if available
            "aliases": aliases,
            "tags": tags,
            "creation_date": key_metadata.get("CreationDate").isoformat() if key_metadata.get("CreationDate") else None,
            "enabled": key_metadata.get("Enabled", True),
            "key_state": key_metadata.get("KeyState", "Unknown")
        }

    except Exception as e:
        print(f"⚠️ Error fetching KMS key {key_id}: {e}")
        return None


# -----------------------
# Function: List all KMS keys
# -----------------------
def list_all_kms_keys():
    """
    List all KMS keys in the account
    """
    try:
        keys = []
        paginator = kms.get_paginator('list_keys')
        
        for page in paginator.paginate():
            for key in page['Keys']:
                # Only include customer-managed keys (not AWS-managed)
                key_desc = kms.describe_key(KeyId=key['KeyId'])
                if key_desc['KeyMetadata'].get('KeyManager') == 'CUSTOMER':
                    keys.append(key['KeyId'])
        
        return keys
    except Exception as e:
        print(f"⚠️ Error listing KMS keys: {e}")
        return []


# -----------------------
# Function: Get all KMS configurations
# -----------------------
def get_all_kms_configs():
    """
    Get configurations for all customer-managed KMS keys
    """
    all_keys = {}
    key_ids = list_all_kms_keys()
    
    for key_id in key_ids:
        config = get_kms_key_config(key_id)
        if config:
            # Use key_id as the key in the dictionary
            all_keys[key_id] = config
    
    return all_keys
