import boto3
from botocore.exceptions import ClientError

secretsmanager = boto3.client("secretsmanager")

# -----------------------
# Function: Get Secret config
# -----------------------
def get_secret_config(secret_id):
    try:
        desc = secretsmanager.describe_secret(SecretId=secret_id)

        # Optional: Get the actual secret value
        # try:
        #     value_response = secretsmanager.get_secret_value(SecretId=secret_id)
        #     secret_value = value_response.get("SecretString") or "<binary or KMS-encrypted value>"
        # except ClientError as e:
        #     secret_value = f"<error retrieving secret value: {e.response['Error']['Message']}>"

        return {
            "name": desc["Name"],
            "arn": desc["ARN"],
            "description": desc.get("Description", ""),
            "kms_key_id": desc.get("KmsKeyId"),
            "rotation_enabled": desc.get("RotationEnabled", False),
            "rotation_lambda_arn": desc.get("RotationLambdaARN"),
            "tags": desc.get("Tags", []),
            # "value": secret_value,  # optional: remove if you don't want to store value
        }

    except Exception as e:
        print(f"⚠️ Error fetching secret {secret_id}: {e}")
        return None
