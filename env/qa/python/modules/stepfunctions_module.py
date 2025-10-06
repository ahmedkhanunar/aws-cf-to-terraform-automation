import boto3
from botocore.exceptions import ClientError, ParamValidationError

# Initialize the Step Functions client
stepfunctions = boto3.client("stepfunctions")


# -----------------------
# Function: Get Step Functions state machine config by ARN
# -----------------------
def get_state_machine_config_by_arn(state_machine_arn):
    try:
        print(f"🔍 Fetching state machine config for ARN: {state_machine_arn}")

        # Correct the parameter name to 'stateMachineArn' (lowercase 's')
        desc = stepfunctions.describe_state_machine(stateMachineArn=state_machine_arn)

        # Tags
        tags = {}
        try:
            tag_resp = stepfunctions.list_tags_for_resource(resourceArn=state_machine_arn)
            tags = {t["key"]: t["value"] for t in tag_resp.get("tags", [])}
        except ClientError as e:
            print(f"⚠️ Warning: Could not retrieve tags for state machine {state_machine_arn}: {e}")

        # Build the config
        config = {
            "name": desc.get("name"),
            "arn": desc.get("stateMachineArn"),
            "definition": desc.get("definition"),
            "role_arn": desc.get("roleArn"),
            "type": desc.get("type"),
            "logging_configuration": desc.get("loggingConfiguration"),
            "tracing_configuration": desc.get("tracingConfiguration"),
            "status": desc.get("status"),
            "creation_date": desc.get("creationDate").isoformat() if desc.get("creationDate") else None,
            "tags": tags,
        }

        return config

    except ParamValidationError as e:
        print(f"⚠️ Parameter validation failed for ARN {state_machine_arn}: {e}")
        return None
    except ClientError as e:
        print(f"⚠️ Client error fetching state machine {state_machine_arn}: {e}")
        return None
    except Exception as e:
        print(f"⚠️ Unexpected error fetching state machine {state_machine_arn}: {e}")
        return None


# -----------------------
# Function: Resolve state machine by name (optional helper)
# -----------------------
def get_state_machine_config_by_name(state_machine_name):
    try:
        paginator = stepfunctions.get_paginator("list_state_machines")

        # Pagination through state machines
        for page in paginator.paginate():
            for sm in page.get("stateMachines", []):
                print(f"🔍 Checking state machine: {sm.get('name')}")  # Debugging line to check each state machine
                if sm.get("name") == state_machine_name:
                    return get_state_machine_config_by_arn(sm.get("stateMachineArn"))

        print(f"⚠️ No state machine found with name: {state_machine_name}")
        return None
    except ClientError as e:
        print(f"⚠️ Client error listing Step Functions state machines: {e}")
        return None
    except Exception as e:
        print(f"⚠️ Unexpected error listing state machines: {e}")
        return None

