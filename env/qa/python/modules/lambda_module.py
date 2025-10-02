import os
import boto3
from helpers import download_lambda_code

lambda_client = boto3.client("lambda")

# -----------------------
# Function: Get Lambda config
# -----------------------

def get_lambda_config(function_name):
    try:
        response = lambda_client.get_function(FunctionName=function_name)
        func = response["Configuration"]
        code = response.get("Code", {})

        # Get VPC config
        vpc_config = func.get("VpcConfig", {})
        vpc_info = {
            "subnet_ids": vpc_config.get("SubnetIds", []),
            "security_group_ids": vpc_config.get("SecurityGroupIds", []),
            "vpc_id": vpc_config.get("VpcId", None),
        }

        # Get DLQ
        dlq_target = func.get("DeadLetterConfig", {}).get("TargetArn")

        # Tracing
        tracing_mode = func.get("TracingConfig", {}).get("Mode", "PassThrough")

        # Layers
        layers = [layer["Arn"] for layer in func.get("Layers", [])]

        # Fetch aliases
        aliases_response = lambda_client.list_aliases(FunctionName=function_name)
        aliases = [
            {
                "name": alias["Name"],
                "description": alias.get("Description", ""),
                "function_version": alias.get("FunctionVersion")
            }
            for alias in aliases_response.get("Aliases", [])
        ]

        # Download code if Zip type
        local_code_path = None
        if func.get("PackageType") == "Zip" and "Location" in code:
            os.makedirs("code", exist_ok=True)
            local_code_path = f"code/{function_name}.zip"
            try:
                print('')
                # download_lambda_code(code["Location"], local_code_path)
            except Exception as e:
                print(f"⚠️ Failed to download Lambda code: {e}")
                local_code_path = None

        return {
            "function_name": func["FunctionName"],
            "runtime": func.get("Runtime"),
            "handler": func.get("Handler"),
            "role": func.get("Role"),
            "description": func.get("Description", ""),
            "memory_size": func.get("MemorySize"),
            "timeout": func.get("Timeout"),
            "last_modified": func.get("LastModified"),
            "region": lambda_client.meta.region_name,
            "environment": func.get("Environment", {}).get("Variables", {}),
            "architectures": func.get("Architectures", []),
            "ephemeral_storage": func.get("EphemeralStorage", {}).get("Size", 512),
            "kms_key_arn": func.get("KMSKeyArn"),
            "layers": layers,
            "vpc_config": vpc_info,
            "dead_letter_queue": dlq_target,
            "tracing_mode": tracing_mode,
            "package_type": func.get("PackageType", "Zip"),
            "image_config": func.get("ImageConfigResponse", {}),
            "code_sha256": func.get("CodeSha256"),
            "code_size": func.get("CodeSize"),
            "publish_version": True if func.get("Version") != "$LATEST" else False,
            "version": func.get("Version"),
            "aliases": aliases,
            "dummy_filename": local_code_path
        }

    except Exception as e:
        print(f"⚠️ Error fetching Lambda {function_name}: {e}")
        return None
