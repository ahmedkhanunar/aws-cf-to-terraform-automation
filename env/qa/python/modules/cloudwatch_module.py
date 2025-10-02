# modules/cloudwatch_module.py

import boto3

logs = boto3.client("logs")


def format_tags(tag_list):
    """Convert AWS tag list to Terraform-style key-value dict."""
    return {tag["key"]: tag["value"] for tag in tag_list}


def get_log_group_config(log_group_name):
    """Fetch log group config and tags."""
    try:
        response = logs.describe_log_groups(logGroupNamePrefix=log_group_name, limit=1)
        if not response["logGroups"]:
            return None

        log_group = response["logGroups"][0]
        result = {
            "name": log_group["logGroupName"],
            "retention_in_days": log_group.get("retentionInDays", None),
            "kms_key_id": log_group.get("kmsKeyId", None),
            "tags": {}
        }

        # Get tags
        try:
            tag_resp = logs.list_tags_log_group(logGroupName=log_group_name)
            result["tags"] = tag_resp.get("tags", {})
        except Exception as tag_err:
            print(f"⚠️ Failed to get tags for log group {log_group_name}: {tag_err}")

        return result

    except Exception as e:
        print(f"⚠️ Error getting log group {log_group_name}: {e}")
        return None

