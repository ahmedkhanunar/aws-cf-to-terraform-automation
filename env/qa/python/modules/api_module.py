import boto3

# Create clients for both apigateway (REST APIs) and apigatewayv2 (HTTP/WebSocket APIs)
apigateway = boto3.client("apigateway")
apigatewayv2 = boto3.client("apigatewayv2")

def get_resources_paginated(api_id, api_type="REST"):
    """Fetch all resources or routes with pagination for REST or HTTP/WebSocket APIs."""
    resources = []
    next_token = None

    if api_type == "REST":
        while True:
            if next_token:
                response = apigateway.get_resources(
                    restApiId=api_id,
                    position=next_token
                )
            else:
                response = apigateway.get_resources(restApiId=api_id)

            resources.extend(response.get('items', []))
            next_token = response.get('position')
            if not next_token:
                break

    elif api_type in ["HTTP", "WEBSOCKET"]:
        while True:
            if next_token:
                response = apigatewayv2.get_routes(
                    ApiId=api_id,
                    NextToken=next_token
                )
            else:
                response = apigatewayv2.get_routes(ApiId=api_id)

            resources.extend(response.get('Items', []))
            next_token = response.get('NextToken')
            if not next_token:
                break

    return resources


def get_api_config(api_id, api_type="REST"):
    """Fetch API Gateway API, resources, and methods configuration for REST/HTTP/WebSocket APIs."""
    try:
        # Get API details (general information about the API)
        if api_type == "REST":
            api_response = apigateway.get_rest_api(restApiId=api_id)
        elif api_type in ["HTTP", "WEBSOCKET"]:
            api_response = apigatewayv2.get_api(ApiId=api_id)

        # Get all resources or routes (handling pagination)
        resources = get_resources_paginated(api_id, api_type)

        # Initialize methods dictionary to store methods for each resource or route
        methods = {}

        if api_type == "REST":
            for resource in resources:
                resource_id = resource["id"]
                resource_methods = {}

                # Check if the resource has any methods (e.g., POST, GET)
                if "resourceMethods" in resource:
                    for method in resource["resourceMethods"]:
                        method_name = method  # e.g., "POST", "GET"
                        method_details = apigateway.get_method(
                            restApiId=api_id,
                            resourceId=resource_id,
                            httpMethod=method_name
                        )
                        resource_methods[method_name] = {
                            "authorization_type": method_details.get("authorizationType"),
                            "integration": method_details.get("methodIntegration", {})
                        }

                methods[resource_id] = resource_methods

        elif api_type in ["HTTP", "WEBSOCKET"]:
            # HTTP/WebSocket APIs do not have resourceMethods like REST APIs
            for route in resources:
                route_id = route["RouteId"]
                route_methods = {
                    "GET": {},  # or other methods if applicable
                    "POST": {}, 
                    # Depending on API, you can add other methods as needed
                }

                # For each route, fetch the integration details (if any)
                for method in route_methods:
                    integration_response = apigatewayv2.get_integration(
                        ApiId=api_id,
                        IntegrationId=route["RouteKey"]
                    )
                    route_methods[method] = {
                        "integration": integration_response.get("IntegrationUri", "N/A")
                    }

                methods[route_id] = route_methods

        # Get stages for the API
        if api_type == "REST":
            stages_response = apigateway.get_stages(restApiId=api_id)
            stages = stages_response.get("item", [])
        elif api_type in ["HTTP", "WEBSOCKET"]:
            stages_response = apigatewayv2.get_stages(ApiId=api_id)
            stages = stages_response.get("Items", [])

        # Return combined API configuration (API, resources, methods, stages)
        return {
            "api": api_response,
            "resources": resources,
            "methods": methods,
            "stages": stages
        }

    except Exception as e:
        print(f"⚠️ Failed to get API Gateway configuration for API {api_id}: {e}")
        return None


def flatten_api_gateway_resources(data):
    """Flatten API Gateway data for Terraform modules."""
    result = {
        "apis": {},
        "resources": {},
        "methods": {},
        "stages": {}
    }

    # Flatten APIs (for all types)
    for api_id, api_data in data.get("apis", {}).items():
        result["apis"][api_id] = {
            "name": api_data["name"],
            "description": api_data.get("description"),
            "endpoint_type": api_data.get("endpointConfiguration", {}).get("types", [])
        }

        # Flatten resources (handle REST, HTTP, WebSocket differently)
        for resource in data.get("resources", {}).get(api_id, []):
            resource_id = resource["id"]
            result["resources"][resource_id] = {
                **resource,
                "method": {}
            }

            # Flatten methods (for REST)
            if api_data.get("endpoint_type", ["REGIONAL"])[0] == "REGIONAL":
                for method_id, method_data in data.get("methods", {}).get(api_id, {}).items():
                    result["resources"][resource_id]["method"][method_id] = method_data

        # Flatten stages
        for stage in data.get("stages", {}).get(api_id, []):
            result["stages"][stage["stageName"]] = {
                "deployment_id": stage["deploymentId"],
                "variables": stage.get("variables", {}),
                "description": stage.get("description")
            }

    return result
