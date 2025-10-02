# modules/cognito_module.py

import boto3
from botocore.exceptions import ClientError

cognito_idp = boto3.client("cognito-idp")
cognito_identity = boto3.client("cognito-identity")


def get_user_pool_config(pool_id):
    try:
        response = cognito_idp.describe_user_pool(UserPoolId=pool_id)["UserPool"]
        tags = cognito_idp.list_tags_for_resource(
            ResourceArn=response["Arn"]
        ).get("Tags", {})

        return {
            "name": response["Name"],
            "id": pool_id,
            "arn": response["Arn"],
            "policies": response.get("Policies", {}),
            "mfa_configuration": response.get("MfaConfiguration", "OFF"),
            "tags": tags
        }

    except ClientError as e:
        print(f"⚠️ Failed to describe user pool {pool_id}: {e}")
        return None


def get_user_pool_client_config(pool_id, client_id):
    try:
        client = cognito_idp.describe_user_pool_client(
            UserPoolId=pool_id,
            ClientId=client_id
        )["UserPoolClient"]

        return {
            "client_id": client["ClientId"],
            "name": client["ClientName"],
            "user_pool_id": client["UserPoolId"],
            "explicit_auth_flows": client.get("ExplicitAuthFlows", []),
            "allowed_oauth_flows": client.get("AllowedOAuthFlows", []),
            "callback_urls": client.get("CallbackURLs", []),
            "logout_urls": client.get("LogoutURLs", []),
            "supported_identity_providers": client.get("SupportedIdentityProviders", [])
        }

    except ClientError as e:
        print(f"⚠️ Failed to get user pool client {client_id}: {e}")
        return None


def get_identity_pool_config(identity_pool_id):
    try:
        identity_pool = cognito_identity.describe_identity_pool(
            IdentityPoolId=identity_pool_id
        )
        return {
            "identity_pool_id": identity_pool["IdentityPoolId"],
            "identity_pool_name": identity_pool["IdentityPoolName"],
            "allow_unauthenticated_identities": identity_pool.get("AllowUnauthenticatedIdentities", False),
            "cognito_identity_providers": identity_pool.get("CognitoIdentityProviders", [])
        }

    except ClientError as e:
        print(f"⚠️ Failed to describe identity pool {identity_pool_id}: {e}")
        return None


def find_user_pool_for_client(client_id):
    """Brute force search to find which User Pool owns the given client_id."""
    try:
        paginator = cognito_idp.get_paginator("list_user_pools")
        for page in paginator.paginate(MaxResults=60):
            for pool in page["UserPools"]:
                pool_id = pool["Id"]
                try:
                    _ = cognito_idp.describe_user_pool_client(
                        UserPoolId=pool_id,
                        ClientId=client_id
                    )
                    return pool_id  # Found the pool
                except ClientError as e:
                    if e.response["Error"]["Code"] != "ResourceNotFoundException":
                        print(f"⚠️ Unexpected error while checking pool {pool_id}: {e}")
                    continue
    except Exception as e:
        print(f"⚠️ Error finding user pool for client {client_id}: {e}")
    return None
