# modules/sqs_module.py

import boto3
from botocore.exceptions import ClientError
import datetime


def json_safe(data):
    """Convert datetime and other non-serializable types to string."""
    if isinstance(data, dict):
        return {k: json_safe(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [json_safe(item) for item in data]
    elif isinstance(data, datetime.datetime):
        return data.isoformat()
    return data


def get_sqs_client():
    return boto3.client("sqs")


def get_sqs_queue_config(queue_url_or_name):
    client = get_sqs_client()

    try:
        # Convert name to URL if needed
        if not queue_url_or_name.startswith("https://"):
            # List all queues and match by name
            response = client.list_queues()
            urls = response.get("QueueUrls", [])
            match = next((url for url in urls if url.endswith(queue_url_or_name)), None)
            if not match:
                print(f"❌ Could not resolve URL for queue {queue_url_or_name}")
                return None
            queue_url = match
        else:
            queue_url = queue_url_or_name

        attributes_response = client.get_queue_attributes(
            QueueUrl=queue_url,
            AttributeNames=["All"]
        )
        attributes = attributes_response.get("Attributes", {})

        # Add tags
        tags = {}
        try:
            tags_response = client.list_queue_tags(QueueUrl=queue_url)
            tags = tags_response.get("Tags", {})
        except ClientError:
            pass  # Not all queues are tagged

        return json_safe({
            "url": queue_url,
            "name": attributes.get("QueueName") or queue_url.split("/")[-1],
            "arn": attributes.get("QueueArn"),
            "attributes": attributes,
            "tags": tags
        })

    except ClientError as e:
        print(f"❌ Error getting SQS config for {queue_url_or_name}: {e}")
        return None
