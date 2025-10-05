import boto3
import json
from collections import defaultdict

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
        if next_token:
            response = client.describe_stack_resources(StackName=stack_name, NextToken=next_token)
        else:
            response = client.describe_stack_resources(StackName=stack_name)
        
        resources.extend(response['StackResources'])
        
        next_token = response.get('NextToken', None)
        if not next_token:
            break
    
    return resources

def collect_resources():
    """Collect and categorize services and their resource types (without actual resource details)."""
    service_structure = defaultdict(set)  # Use a set to avoid duplicate resource types
    
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
                
                # Categorize resource by full service name (e.g., AWS::Lambda, AWS::CloudFront)
                service_name = "::".join(resource_type.split("::")[:2])  # Get the full service name (e.g., AWS::Lambda)
                
                # Add the sub-resource (e.g., AWS::Lambda::Function) to the service category
                service_structure[service_name].add(resource_type)
    
    return service_structure

def save_resources(resources, filename="cf_stack_services.json"):
    """Save the categorized services and their sub-resources to a JSON file."""
    # Sort services and sub-resources
    sorted_resources = {
        service: sorted(list(resources[service]))  # Sort the sub-resources for each service
        for service in sorted(resources)           # Sort the services alphabetically
    }
    
    with open(filename, 'w') as f:
        json.dump(sorted_resources, f, indent=4)
        print(f"Services and sub-resources saved to {filename}")

if __name__ == "__main__":
    resources = collect_resources()
    save_resources(resources)
