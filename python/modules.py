import os

# Define module names (grouped by resource type)
modules = [
    "s3", "dynamodb", "logs", "cloudwatch",
    "iam", "kms", "secrets_manager",
    "vpc", "subnet", "route_table", "internet_gateway", "nat_gateway", "eip", "flow_log", "nacl",
    "lambda", "lambda_layer", "stepfunctions", "elasticache",
    "apigateway", "cognito", "appflow",
    "sns", "sqs", "events", "scheduler",
    "cloudfront", "cloudtrail", "config",
    "guardduty", "securityhub", "waf",
    "custom"
]

base_dir = "modules"

# Create module directories with TF skeleton
for module in modules:
    path = os.path.join(base_dir, module)
    os.makedirs(path, exist_ok=True)

    # main.tf
    main_tf = os.path.join(path, "main.tf")
    if not os.path.exists(main_tf):
        with open(main_tf, "w") as f:
            f.write(f'// Terraform module: {module}\n')
            f.write('terraform {\n  required_version = ">= 1.0.0"\n}\n\n')
            f.write('resource "" "" {\n  # TODO: define resources\n}\n')

    # variables.tf
    variables_tf = os.path.join(path, "variables.tf")
    if not os.path.exists(variables_tf):
        with open(variables_tf, "w") as f:
            f.write('// Variables for module: {}\n'.format(module))
            f.write('variable "name" {\n  type        = string\n  description = "Name for resource"\n}\n')

    # outputs.tf
    outputs_tf = os.path.join(path, "outputs.tf")
    if not os.path.exists(outputs_tf):
        with open(outputs_tf, "w") as f:
            f.write('// Outputs for module: {}\n'.format(module))
            f.write('output "id" {\n  value       = ""\n  description = "Resource ID"\n}\n')

print("✅ Terraform module skeletons created under 'modules/'")
