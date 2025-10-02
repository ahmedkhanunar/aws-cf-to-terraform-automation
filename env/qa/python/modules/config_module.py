import boto3
import datetime
from botocore.exceptions import ClientError


def json_safe(data):
    """Convert datetime and other non-serializable types to string."""
    if isinstance(data, dict):
        return {k: json_safe(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [json_safe(item) for item in data]
    elif isinstance(data, datetime.datetime):
        return data.isoformat()
    return data


def get_config_client():
    return boto3.client("config")


def get_config_recorder_config(rid):
    client = get_config_client()
    try:
        response = client.describe_configuration_recorders()
        for rec in response.get("ConfigurationRecorders", []):
            if rec["name"] == rid:
                return json_safe(rec)
    except ClientError as e:
        print(f"❌ Error getting recorder config for {rid}: {e}")
    return None


def get_config_recorder_status(rid):
    client = get_config_client()
    try:
        response = client.describe_configuration_recorder_status()
        for status in response.get("ConfigurationRecordersStatus", []):
            if status["name"] == rid:
                return json_safe(status)
    except ClientError as e:
        print(f"❌ Error getting recorder status for {rid}: {e}")
    return None


def get_delivery_channel_config(rid):
    client = get_config_client()
    try:
        response = client.describe_delivery_channels()
        for ch in response.get("DeliveryChannels", []):
            if ch["name"] == rid:
                return json_safe(ch)
    except ClientError as e:
        print(f"❌ Error getting delivery channel for {rid}: {e}")
    return None


def get_delivery_channel_status(rid):
    client = get_config_client()
    try:
        response = client.describe_delivery_channel_status()
        for status in response.get("DeliveryChannelsStatus", []):
            if status["name"] == rid:
                return json_safe(status)
    except ClientError as e:
        print(f"❌ Error getting delivery channel status for {rid}: {e}")
    return None


def get_config_rule_config(rid):
    client = get_config_client()
    try:
        response = client.describe_config_rules()
        for rule in response.get("ConfigRules", []):
            if rule["ConfigRuleName"] == rid:
                return json_safe(rule)
    except ClientError as e:
        print(f"❌ Error getting config rule {rid}: {e}")
    return None


def get_rule_compliance(rid):
    client = get_config_client()
    try:
        response = client.describe_compliance_by_config_rule(ConfigRuleNames=[rid])
        for c in response.get("ComplianceByConfigRules", []):
            if c["ConfigRuleName"] == rid:
                return json_safe(c)
    except ClientError as e:
        print(f"❌ Error getting compliance for rule {rid}: {e}")
    return None
