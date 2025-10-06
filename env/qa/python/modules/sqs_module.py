import boto3
from botocore.exceptions import ClientError
import json

sqs = boto3.client("sqs")

# -----------------------
# Function: Get SQS queue config
# -----------------------
def get_sqs_queue_config(queue_url):
    try:
        # Get queue attributes
        attributes_response = sqs.get_queue_attributes(
            QueueUrl=queue_url,
            AttributeNames=['All']
        )
        attributes = attributes_response.get('Attributes', {})
        
        # Extract queue name from URL
        queue_name = queue_url.split('/')[-1]
        
        # Get queue policy if it exists
        try:
            policy_response = sqs.get_queue_attributes(
                QueueUrl=queue_url,
                AttributeNames=['Policy']
            )
            policy = policy_response.get('Attributes', {}).get('Policy')
        except ClientError as e:
            print(f"⚠️ Warning: Could not retrieve policy for queue {queue_name}: {e}")
            policy = None
        
        # Get tags
        try:
            tags_response = sqs.list_queue_tags(QueueUrl=queue_url)
            tags = tags_response.get('Tags', {})
        except ClientError as e:
            print(f"⚠️ Warning: Could not retrieve tags for queue {queue_name}: {e}")
            tags = {}
        
        # Parse redrive policy if it exists
        redrive_policy = None
        if attributes.get('RedrivePolicy'):
            try:
                redrive_policy_data = json.loads(attributes['RedrivePolicy'])
                redrive_policy = {
                    "dead_letter_target_arn": redrive_policy_data.get('deadLetterTargetArn'),
                    "max_receive_count": redrive_policy_data.get('maxReceiveCount')
                }
            except json.JSONDecodeError:
                print(f"⚠️ Warning: Could not parse redrive policy for queue {queue_name}")
        
        return {
            "name": queue_name,
            "url": queue_url,
            "arn": attributes.get('QueueArn'),
            "delay_seconds": int(attributes.get('DelaySeconds', 0)),
            "max_message_size": int(attributes.get('MaximumMessageSize', 262144)),
            "message_retention_seconds": int(attributes.get('MessageRetentionPeriod', 1209600)),
            "receive_wait_time_seconds": int(attributes.get('ReceiveMessageWaitTimeSeconds', 0)),
            "visibility_timeout_seconds": int(attributes.get('VisibilityTimeout', 30)),
            "sqs_managed_sse_enabled": attributes.get('SqsManagedSseEnabled', 'false').lower() == 'true',
            "kms_master_key_id": attributes.get('KmsMasterKeyId'),
            "kms_data_key_reuse_period_seconds": int(attributes.get('KmsDataKeyReusePeriodSeconds', 300)),
            "fifo_queue": attributes.get('FifoQueue', 'false').lower() == 'true',
            "content_based_deduplication": attributes.get('ContentBasedDeduplication', 'false').lower() == 'true',
            "deduplication_scope": attributes.get('DeduplicationScope'),
            "fifo_throughput_limit": attributes.get('FifoThroughputLimit'),
            "redrive_policy": redrive_policy,
            "policy": policy,
            "tags": tags,
            "created_timestamp": attributes.get('CreatedTimestamp'),
            "last_modified_timestamp": attributes.get('LastModifiedTimestamp')
        }

    except Exception as e:
        print(f"⚠️ Error fetching SQS queue {queue_url}: {e}")
        return None


# -----------------------
# Function: Get SQS queue configuration by physical resource ID
# -----------------------
def get_sqs_queue_config_by_physical_resource_id(physical_resource_id):
    """
    Extract the queue name from the full URL and fetch the SQS queue config.
    """
    # Extract queue name from URL (last part after "/")
    queue_name = physical_resource_id.split('/')[-1]
    
    # Fetch the queue configuration using the queue name
    return get_sqs_queue_config_by_name(queue_name)


# -----------------------
# Function: Get SQS queue by name
# -----------------------
def get_sqs_queue_config_by_name(queue_name):
    """
    Get SQS queue configuration by name
    """
    try:
        # Get queue URL by name
        queue_url_response = sqs.get_queue_url(QueueName=queue_name)
        queue_url = queue_url_response['QueueUrl']
        
        # Fetch the full configuration for the queue
        return get_sqs_queue_config(queue_url)
    
    except Exception as e:
        print(f"⚠️ Error fetching SQS queue by name {queue_name}: {e}")
        return None