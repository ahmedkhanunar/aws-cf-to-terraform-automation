import boto3

cf = boto3.client("cloudformation")

# -----------------------
# Function: List all stacks
# -----------------------
def list_stacks():
    stacks = []
    paginator = cf.get_paginator("list_stacks")
    for page in paginator.paginate(StackStatusFilter=["CREATE_COMPLETE", "UPDATE_COMPLETE"]):
        for stack in page["StackSummaries"]:
            stacks.append(stack["StackName"])
    return stacks

# -----------------------
# Function: List stack resources
# -----------------------
def list_stack_resources(stack_name):
    resources = []
    paginator = cf.get_paginator("list_stack_resources")
    for page in paginator.paginate(StackName=stack_name):
        for res in page["StackResourceSummaries"]:
            if res["ResourceStatus"] != "DELETE_COMPLETE":
                resources.append(res)
    return resources
