import boto3
from botocore.exceptions import ClientError
import json

lambda_client = boto3.client("lambda")

# -----------------------
# Function: Get Lambda layer config
# -----------------------
def get_lambda_layer_config(layer_name, version=None):
    try:
        # Get layer versions
        if version:
            # Get specific version
            response = lambda_client.get_layer_version(
                LayerName=layer_name,
                VersionNumber=int(version)
            )
            # print(f"Response for {layer_name} version {version}: {json.dumps(response, indent=2)}")  # Debugging line
            layer_versions = [response]
        else:
            # Get all versions
            paginator = lambda_client.get_paginator('list_layer_versions')
            layer_versions = []
            for page in paginator.paginate(LayerName=layer_name):
                layer_versions.extend(page['LayerVersions'])
        
        if not layer_versions:
            return None
        
        # Get the latest version (highest version number)
        latest_version = max(layer_versions, key=lambda x: x['Version'])
        
        # Get layer configuration for the latest version
        layer_config = lambda_client.get_layer_version(
            LayerName=layer_name,
            VersionNumber=latest_version['Version']
        )
        
        # Directly access the top-level keys in the response
        layer_info = layer_config  # No need for 'LayerVersion' anymore
        
        # Extract the layer name from the ARN if needed (optional)
        layer_name_from_arn = layer_info['LayerArn'].split(':')[-1]  # Extracts the last part of the ARN
        
        return {
            "layer_name": layer_name_from_arn,
            "version": layer_info['Version'],
            "arn": layer_info['LayerVersionArn'],
            "layer_arn": layer_info['LayerArn'],
            "description": layer_info.get('Description', ''),
            "created_date": layer_info.get('CreatedDate', ''),  # No isoformat() call
            "compatible_runtimes": layer_info.get('CompatibleRuntimes', []),
            "compatible_architectures": layer_info.get('CompatibleArchitectures', ['x86_64']),
            "license_info": layer_info.get('LicenseInfo'),
            "code_size": layer_info.get('CodeSize'),
            "signing_profile_version_arn": layer_info.get('SigningProfileVersionArn'),
            "signing_job_arn": layer_info.get('SigningJobArn'),
            "code_sha256": layer_info.get('CodeSha256'),
            "all_versions": [v['Version'] for v in layer_versions]
        }

    except Exception as e:
        # print(f"⚠️ Error fetching Lambda layer {layer_name}: {e}")
        return None

# -----------------------
# Function: List all Lambda layers
# -----------------------
def list_all_lambda_layers():
    """
    List all Lambda layers in the account
    """
    try:
        layers = []
        paginator = lambda_client.get_paginator('list_layers')
        
        for page in paginator.paginate():
            for layer in page['Layers']:
                layers.append({
                    'layer_name': layer['LayerName'],
                    'layer_arn': layer['LayerArn'],
                    'latest_matching_version': layer.get('LatestMatchingVersion', {})
                })
        
        return layers
    except Exception as e:
        # print(f"⚠️ Error listing Lambda layers: {e}")
        return []


# -----------------------
# Function: Get all Lambda layer configurations
# -----------------------
def get_all_lambda_layer_configs():
    """
    Get configurations for all Lambda layers
    """
    all_layers = {}
    layers = list_all_lambda_layers()
    
    for layer_info in layers:
        layer_name = layer_info['layer_name']
        config = get_lambda_layer_config(layer_name)
        if config:
            # Use layer_name as the key in the dictionary
            all_layers[layer_name] = config
    
    return all_layers


# -----------------------
# Function: Get Lambda layer by ARN
# -----------------------
def get_lambda_layer_config_by_arn(layer_arn):
    """
    Get Lambda layer configuration by ARN
    """
    try:
        # Extract layer name and version from ARN
        # ARN format: arn:aws:lambda:region:account:layer:layer-name:version
        arn_parts = layer_arn.split(':')
        if len(arn_parts) < 8:
            # print(f"⚠️ Invalid layer ARN format: {layer_arn}")
            return None
        
        layer_name = arn_parts[6]
        version = arn_parts[7] if len(arn_parts) > 7 else None
        
        return get_lambda_layer_config(layer_name, version)
    
    except Exception as e:
        # print(f"⚠️ Error fetching Lambda layer by ARN {layer_arn}: {e}")
        return None
