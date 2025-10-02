import json
import os
import requests
from botocore.exceptions import ClientError

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
