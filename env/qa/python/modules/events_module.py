import boto3
from botocore.exceptions import ClientError
import json

events = boto3.client("events")

# -----------------------
# Function: Get EventBridge rule config
# -----------------------
def get_event_rule_config(rule_name):
    try:
        # Get rule details
        rule_response = events.describe_rule(Name=rule_name)
        rule = rule_response
        
        # Get targets for this rule
        targets_response = events.list_targets_by_rule(Rule=rule_name)
        targets = targets_response.get('Targets', [])
        
        # Process targets
        processed_targets = []
        for target in targets:
            target_config = {
                "target_id": target.get('Id'),
                "arn": target.get('Arn'),
                "input": target.get('Input'),
                "input_path": target.get('InputPath'),
                "role_arn": target.get('RoleArn')
            }
            
            # Handle ECS targets
            if 'EcsParameters' in target:
                ecs_params = target['EcsParameters']
                target_config["ecs_target"] = {
                    "task_definition_arn": ecs_params.get('TaskDefinitionArn'),
                    "launch_type": ecs_params.get('LaunchType'),
                    "network_configuration": {
                        "subnets": ecs_params.get('NetworkConfiguration', {}).get('awsvpcConfiguration', {}).get('Subnets', []),
                        "security_groups": ecs_params.get('NetworkConfiguration', {}).get('awsvpcConfiguration', {}).get('SecurityGroups', []),
                        "assign_public_ip": ecs_params.get('NetworkConfiguration', {}).get('awsvpcConfiguration', {}).get('AssignPublicIp', False)
                    }
                }
            
            # Lambda targets are handled by the input parameter above
            
            processed_targets.append(target_config)
        
        # Get tags
        tags = {}
        try:
            tags_response = events.list_tags_for_resource(ResourceARN=rule.get('Arn'))
            tags = {tag['Key']: tag['Value'] for tag in tags_response.get('Tags', [])}
        except ClientError as e:
            print(f"⚠️ Warning: Could not retrieve tags for rule {rule_name}: {e}")
        
        return {
            "name": rule.get('Name'),
            "arn": rule.get('Arn'),
            "description": rule.get('Description', ''),
            "schedule_expression": rule.get('ScheduleExpression'),
            "event_pattern": rule.get('EventPattern'),
            "role_arn": rule.get('RoleArn'),
            "is_enabled": rule.get('State') == 'ENABLED',
            "event_bus_name": rule.get('EventBusName', 'default'),
            "targets": processed_targets[0] if processed_targets else None,
            "all_targets": processed_targets,
            "tags": tags,
            "created_date": rule.get('CreatedDate').isoformat() if rule.get('CreatedDate') else None
        }

    except Exception as e:
        print(f"⚠️ Error fetching EventBridge rule {rule_name}: {e}")
        return None


# -----------------------
# Function: List all EventBridge rules
# -----------------------
def list_all_event_rules():
    """
    List all EventBridge rules in the account
    """
    try:
        rules = []
        paginator = events.get_paginator('list_rules')
        
        for page in paginator.paginate():
            for rule in page['Rules']:
                rules.append(rule['Name'])
        
        return rules
    except Exception as e:
        print(f"⚠️ Error listing EventBridge rules: {e}")
        return []


# -----------------------
# Function: Get all EventBridge rule configurations
# -----------------------
def get_all_event_rule_configs():
    """
    Get configurations for all EventBridge rules
    """
    all_rules = {}
    rule_names = list_all_event_rules()
    
    for rule_name in rule_names:
        config = get_event_rule_config(rule_name)
        if config:
            # Use rule_name as the key in the dictionary
            all_rules[rule_name] = config
    
    return all_rules


# -----------------------
# Function: Get EventBridge rule by ARN
# -----------------------
def get_event_rule_config_by_arn(rule_arn):
    """
    Get EventBridge rule configuration by ARN
    """
    try:
        # Extract rule name from ARN
        # ARN format: arn:aws:events:region:account:rule/rule-name
        rule_name = rule_arn.split('/')[-1]
        
        return get_event_rule_config(rule_name)
    
    except Exception as e:
        print(f"⚠️ Error fetching EventBridge rule by ARN {rule_arn}: {e}")
        return None
