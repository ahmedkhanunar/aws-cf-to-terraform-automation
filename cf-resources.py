import boto3
import json

def get_all_stacks():
    """Get all CloudFormation stacks."""
    client = boto3.client('cloudformation')
    stacks = []
    paginator = client.get_paginator('describe_stacks')
    
    for page in paginator.paginate():
        stacks.extend(page['Stacks'])
    
    return stacks

def get_stack_resources(stack_name):
    """Get resources for a specific CloudFormation stack with pagination handling."""
    client = boto3.client('cloudformation')
    resources = []
    next_token = None
    
    while True:
        # Make the describe_stack_resources call
        if next_token:
            response = client.describe_stack_resources(StackName=stack_name, NextToken=next_token)
        else:
            response = client.describe_stack_resources(StackName=stack_name)
        
        resources.extend(response['StackResources'])
        
        # Check if there is a next token to continue pagination
        next_token = response.get('NextToken', None)
        if not next_token:
            break  # No more resources to fetch, exit the loop
    
    return resources

def collect_resources():
    """Collect resources from all stacks."""
    all_resources = set()  # Use set to ensure uniqueness
    
    # Get all stacks
    stacks = get_all_stacks()
    
    for stack in stacks:
        stack_name = stack['StackName']
        stack_status = stack['StackStatus']
        
        # Only process complete or updated stacks
        if stack_status not in ['DELETE_IN_PROGRESS', 'ROLLBACK_IN_PROGRESS', 'DELETE_COMPLETE']:
            resources = get_stack_resources(stack_name)
            
            for resource in resources:
                resource_type = resource['ResourceType']
                physical_resource_id = resource['PhysicalResourceId']
                
                # Add resource details to the unique resources set
                resource_info = {
                    'ResourceType': resource_type,
                    'PhysicalResourceId': physical_resource_id,
                }
                
                # Convert dictionary to a tuple for immutability and uniqueness
                all_resources.add(json.dumps(resource_info, sort_keys=True))
    
    # Convert set back to a list of dicts
    final_resources = [json.loads(resource) for resource in all_resources]
    
    return final_resources

def save_resources(resources, filename="cf_stack_resources.json"):
    """Save resources to a JSON file."""
    with open(filename, 'w') as f:
        json.dump(resources, f, indent=4)
        print(f"Resources saved to {filename}")

if __name__ == "__main__":
    resources = collect_resources()
    save_resources(resources)
