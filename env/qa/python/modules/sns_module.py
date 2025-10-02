# modules/sns_module.py
import boto3

sns = boto3.client("sns")

def get_sns_topic_config(topic_arn):
    try:
        attrs = sns.get_topic_attributes(TopicArn=topic_arn)["Attributes"]
        tags = sns.list_tags_for_resource(ResourceArn=topic_arn).get("Tags", [])
        subs_response = sns.list_subscriptions_by_topic(TopicArn=topic_arn)
        subscriptions = []

        for sub in subs_response.get("Subscriptions", []):
            if sub["SubscriptionArn"] != "PendingConfirmation":
                subscriptions.append({
                    "protocol": sub["Protocol"],
                    "endpoint": sub["Endpoint"],
                    "subscription_arn": sub["SubscriptionArn"],
                    "topic_arn": sub["TopicArn"]
                })

        return {
            "name": attrs["TopicArn"].split(":")[-1],
            "arn": attrs["TopicArn"],
            "display_name": attrs.get("DisplayName"),
            "fifo_topic": attrs.get("FifoTopic") == "true",
            "content_based_deduplication": attrs.get("ContentBasedDeduplication") == "true",
            "tags": tags,
            "subscriptions": subscriptions
        }

    except Exception as e:
        print(f"⚠️ Failed to get SNS topic {topic_arn}: {e}")
        return None

