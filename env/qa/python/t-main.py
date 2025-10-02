import boto3
import json
from datetime import datetime

def get_aws_account_id():
    """Get the AWS Account ID using STS."""
    sts_client = boto3.client('sts')
    identity = sts_client.get_caller_identity()
    return identity['Account']

def get_stacks_in_completed_state():
    """Get stacks that are in a completed state."""
    client = boto3.client('cloudformation')
    stacks = client.describe_stacks()
    completed_stacks = []
    
    for stack in stacks['Stacks']:
        if stack['StackStatus'] in ['CREATE_COMPLETE', 'UPDATE_COMPLETE']:
            completed_stacks.append(stack['StackName'])
    
    return completed_stacks

def get_resources_in_stack(stack_name):
    """Get resources in a stack that are in a completed state."""
    client = boto3.client('cloudformation')
    resources = client.describe_stack_resources(StackName=stack_name)
    completed_resources = []
    
    for resource in resources['StackResources']:
        if resource['ResourceStatus'] in ['CREATE_COMPLETE', 'UPDATE_COMPLETE']:
            completed_resources.append(resource)
    
    return completed_resources

def get_iam_resource_details(arn):
    """Fetch details of IAM resources like roles and policies."""
    client = boto3.client('iam')
    try:
        if 'policy' in arn:
            # Extract the policy ARN and get its details
            policy_details = client.get_policy(PolicyArn=arn)
            return policy_details['Policy']
        elif 'role' in arn:
            # Extract the role ARN and get its details
            role_details = client.get_role(RoleName=arn.split('/')[-1])
            return role_details['Role']
        else:
            return None
    except client.exceptions.NoSuchEntityException:
        print(f"Resource {arn} does not exist or has been deleted.")
        return None

def fetch_iam_resources(stack_name):
    """Fetch IAM resources for a given stack."""
    # Get the AWS Account ID (This is a global ID for all resources)
    account_id = get_aws_account_id()

    # Get the list of resources in the stack
    resources = get_resources_in_stack(stack_name)

    # Filter IAM resources (policies and roles)
    iam_resources = {}

    for resource in resources:
        if resource['ResourceType'] == 'AWS::IAM::Policy':
            arn = f"arn:aws:iam::{account_id}:policy/{resource['PhysicalResourceId']}"
            policy_details = get_iam_resource_details(arn)
            if policy_details:
                iam_resources[resource['PhysicalResourceId']] = policy_details
        elif resource['ResourceType'] == 'AWS::IAM::Role':
            arn = f"arn:aws:iam::{account_id}:role/{resource['PhysicalResourceId']}"
            role_details = get_iam_resource_details(arn)
            if role_details:
                iam_resources[resource['PhysicalResourceId']] = role_details

    return iam_resources

def convert_datetime_to_str(obj):
    """Convert datetime objects to strings."""
    if isinstance(obj, datetime):
        return obj.isoformat()  # Convert datetime to ISO 8601 format
    raise TypeError(f"Type {obj.__class__.__name__} not serializable")

def main():
    # Get the list of stacks that are in the completed state
    completed_stacks = get_stacks_in_completed_state()
    all_iam_resources = {}

    for stack_name in completed_stacks:
        print(f"Fetching IAM resources for stack: {stack_name}")
        
        # Get IAM resources for the stack
        iam_resources = fetch_iam_resources(stack_name)
        if iam_resources:
            all_iam_resources[stack_name] = iam_resources

    # Save the IAM resources to a JSON file
    with open('iam_resources.json', 'w') as json_file:
        json.dump(all_iam_resources, json_file, default=convert_datetime_to_str, indent=4)

    print(f"Completed fetching IAM resources. Saved to 'iam_resources.json'.")

if __name__ == '__main__':
    main()
