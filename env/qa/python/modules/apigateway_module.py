import boto3
from botocore.exceptions import ClientError
import re

apigw = boto3.client("apigateway")
sts = boto3.client("sts")


def list_rest_apis():
    apis = {}
    paginator = apigw.get_paginator("get_rest_apis")
    for page in paginator.paginate():
        for item in page.get("items", []):
            apis[item["id"]] = {
                "id": item.get("id"),
                "name": item.get("name"),
                "description": item.get("description"),
                "api_key_source": item.get("apiKeySource"),
                "endpoint_configuration": item.get("endpointConfiguration", {}),
                "binary_media_types": item.get("binaryMediaTypes", []),
                "minimum_compression_size": item.get("minimumCompressionSize"),
                "policy": item.get("policy"),
                "tags": item.get("tags", {}),
                "version": item.get("version"),
                "warnings": item.get("warnings", []),
            }
    return apis


def extract_rest_api_id_from_rid(physical_resource_id):
    if not physical_resource_id:
        return None
    # Try to parse from common CFN physical IDs
    m = re.search(r"/restapis/([a-z0-9]+)/", physical_resource_id)
    if m:
        return m.group(1)
    # Stage physical id variant: restapiid/stagename
    m2 = re.match(r"^([a-z0-9]{10})/", physical_resource_id)
    if m2:
        return m2.group(1)
    # If the id itself looks like an API id
    if re.match(r"^[a-z0-9]{10}$", physical_resource_id):
        return physical_resource_id
    return None


def get_rest_api_config_by_id(api_id):
    try:
        item = apigw.get_rest_api(restApiId=api_id)
        return {
            "id": item.get("id"),
            "name": item.get("name"),
            "description": item.get("description"),
            "api_key_source": item.get("apiKeySource"),
            "endpoint_configuration": item.get("endpointConfiguration", {}),
            "binary_media_types": item.get("binaryMediaTypes", []),
            "minimum_compression_size": item.get("minimumCompressionSize"),
            "policy": item.get("policy"),
            "tags": item.get("tags", {}),
            "version": item.get("version"),
            "warnings": item.get("warnings", []),
        }
    except ClientError as e:
        print(f"⚠️ Error getting RestApi {api_id}: {e}")
        return None


def get_account():
    try:
        resp = apigw.get_account()
        # Remove response metadata
        resp.pop("ResponseMetadata", None)
        try:
            identity = sts.get_caller_identity()
            resp["account_id"] = identity.get("Account")
        except Exception as e:
            print(f"⚠️ Warning: Could not retrieve STS identity for account id: {e}")
        return resp
    except ClientError as e:
        print(f"⚠️ Error getting API Gateway account: {e}")
        return None


def list_domain_names():
    domains = {}
    paginator = apigw.get_paginator("get_domain_names")
    for page in paginator.paginate():
        for d in page.get("items", []):
            key = d.get("domainName")
            domains[key] = {
                "domain_name": d.get("domainName"),
                "certificate_arn": d.get("certificateArn"),
                "certificate_name": d.get("certificateName"),
                "certificate_upload_date": d.get("certificateUploadDate").isoformat() if d.get("certificateUploadDate") else None,
                "distribution_domain_name": d.get("distributionDomainName"),
                "distribution_hosted_zone_id": d.get("distributionHostedZoneId"),
                "regional_domain_name": d.get("regionalDomainName"),
                "regional_hosted_zone_id": d.get("regionalHostedZoneId"),
                "regional_certificate_arn": d.get("regionalCertificateArn"),
                "regional_certificate_name": d.get("regionalCertificateName"),
                "endpoint_configuration": d.get("endpointConfiguration", {}),
                "mutual_tls_authentication": d.get("mutualTlsAuthentication", {}),
                "security_policy": d.get("securityPolicy"),
                "tags": d.get("tags", {}),
            }
    return domains


def get_domain_name_config(domain_name):
    try:
        d = apigw.get_domain_name(domainName=domain_name)
        return {
            "domain_name": d.get("domainName"),
            "certificate_arn": d.get("certificateArn"),
            "certificate_name": d.get("certificateName"),
            "certificate_upload_date": d.get("certificateUploadDate").isoformat() if d.get("certificateUploadDate") else None,
            "distribution_domain_name": d.get("distributionDomainName"),
            "distribution_hosted_zone_id": d.get("distributionHostedZoneId"),
            "regional_domain_name": d.get("regionalDomainName"),
            "regional_hosted_zone_id": d.get("regionalHostedZoneId"),
            "regional_certificate_arn": d.get("regionalCertificateArn"),
            "regional_certificate_name": d.get("regionalCertificateName"),
            "endpoint_configuration": d.get("endpointConfiguration", {}),
            "mutual_tls_authentication": d.get("mutualTlsAuthentication", {}),
            "security_policy": d.get("securityPolicy"),
            "tags": d.get("tags", {}),
        }
    except ClientError as e:
        print(f"⚠️ Error getting domain name {domain_name}: {e}")
        return None


def list_stages_for_api(rest_api_id):
    stages = {}
    try:
        resp = apigw.get_stages(restApiId=rest_api_id)
        for s in resp.get("item", []):
            name = s.get("stageName")
            stages[name] = {
                "rest_api_id": rest_api_id,
                "stage_name": s.get("stageName"),
                "deployment_id": s.get("deploymentId"),
                "description": s.get("description"),
                "cache_cluster_enabled": s.get("cacheClusterEnabled"),
                "cache_cluster_size": s.get("cacheClusterSize"),
                "variables": s.get("variables", {}),
                "documentation_version": s.get("documentationVersion"),
                "access_log_settings": s.get("accessLogSettings"),
                "canary_settings": s.get("canarySettings"),
                "tracing_enabled": s.get("tracingEnabled"),
                "tags": s.get("tags", {}),
                "web_acl_arn": s.get("webAclArn"),
                "method_settings": s.get("methodSettings", []) if isinstance(s.get("methodSettings"), list) else [],
            }
    except ClientError as e:
        print(f"⚠️ Error listing stages for API {rest_api_id}: {e}")
    return stages


def list_all_stages(rest_api_ids):
    all_stages = {}
    for api_id in rest_api_ids:
        all_stages[api_id] = list_stages_for_api(api_id)
    return all_stages


def parse_stage_from_rid(physical_resource_id):
    if not physical_resource_id:
        return None, None
    # Common CFN Stage id: restapiid/stagename
    m = re.match(r"^([a-z0-9]{10})/([A-Za-z0-9_\-]+)$", physical_resource_id)
    if m:
        return m.group(1), m.group(2)
    # If rid looks like a stage name only, return as stage with unknown api
    if re.match(r"^[A-Za-z0-9_\-]+$", physical_resource_id):
        return None, physical_resource_id
    # Embedded in ARN path format
    m2 = re.search(r"/restapis/([a-z0-9]+)/stages/([A-Za-z0-9_\-]+)", physical_resource_id)
    if m2:
        return m2.group(1), m2.group(2)
    return None, None


def find_stage_config(api_ids, stage_name):
    for api_id in api_ids:
        stages = list_stages_for_api(api_id)
        if stage_name in stages:
            return api_id, stages[stage_name]
    return None, None


def list_resources_for_api(rest_api_id):
    resources = {}
    try:
        paginator = apigw.get_paginator("get_resources")
        for page in paginator.paginate(restApiId=rest_api_id, embed=["methods"]):
            for r in page.get("items", []):
                rid = r.get("id")
                # skip root resource (no pathPart)
                if r.get("pathPart") is None:
                    continue
                resources[rid] = {
                    "rest_api_id": rest_api_id,
                    "id": rid,
                    "parent_id": r.get("parentId"),
                    "path": r.get("path"),
                    "path_part": r.get("pathPart"),
                    "resource_methods": r.get("resourceMethods", {}),
                }
    except ClientError as e:
        print(f"⚠️ Error listing resources for API {rest_api_id}: {e}")
    return resources


def find_resources_by_ids(resource_ids):
    found = {}
    try:
        apis = list_rest_apis()
        for api_id in apis.keys():
            api_resources = list_resources_for_api(api_id)
            for rid, cfg in api_resources.items():
                if rid in resource_ids:
                    found[rid] = cfg
    except Exception as e:
        print(f"⚠️ Error finding resources by ids: {e}")
    return found


