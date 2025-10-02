# modules/cloudtrail_module.py

import boto3

ct = boto3.client("cloudtrail")

def format_tags(tag_list):
    """Convert AWS tag list to Terraform-style list of maps."""
    return [{"Key": tag["Key"], "Value": tag["Value"]} for tag in tag_list]

def get_cloudtrail_config(trail_name):
    try:
        response = ct.get_trail(Name=trail_name)
        trail = response.get("Trail", {})

        # Get logging status
        status = ct.get_trail_status(Name=trail_name)

        # Get trail tags
        tags = []
        try:
            tag_response = ct.list_tags(ResourceIdList=[trail["TrailARN"]])
            tags = tag_response["ResourceTagList"][0].get("TagsList", [])
        except Exception as tag_err:
            print(f"⚠️ Failed to get tags for CloudTrail {trail_name}: {tag_err}")

        # Convert datetime fields to ISO format if present
        latest_delivery_time = status.get("LatestDeliveryTime", None)
        if latest_delivery_time is not None:
            latest_delivery_time = latest_delivery_time.isoformat()

        return {
            "name": trail.get("Name"),
            "s3_bucket_name": trail.get("S3BucketName"),
            "s3_key_prefix": trail.get("S3KeyPrefix"),
            "sns_topic_name": trail.get("SnsTopicName"),
            "include_global_service_events": trail.get("IncludeGlobalServiceEvents", True),
            "is_multi_region_trail": trail.get("IsMultiRegionTrail", False),
            "home_region": trail.get("HomeRegion"),
            "log_file_validation_enabled": trail.get("LogFileValidationEnabled", False),
            "cloud_watch_logs_log_group_arn": trail.get("CloudWatchLogsLogGroupArn"),
            "cloud_watch_logs_role_arn": trail.get("CloudWatchLogsRoleArn"),
            "kms_key_id": trail.get("KmsKeyId"),
            "has_custom_events_selectors": trail.get("HasCustomEventSelectors", False),
            "is_organization_trail": trail.get("IsOrganizationTrail", False),
            "logging": status.get("IsLogging", False),
            "latest_delivery_time": latest_delivery_time,
            "tags": format_tags(tags),
        }

    except Exception as e:
        print(f"⚠️ Failed to get CloudTrail {trail_name}: {e}")
        return None
