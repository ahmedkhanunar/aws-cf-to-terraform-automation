# modules/cloudfront_module.py

import boto3

cloudfront = boto3.client("cloudfront")

def format_tags(tag_response):
    """Convert AWS tag response to list of tag dicts."""
    return [{"Key": tag["Key"], "Value": tag["Value"]} for tag in tag_response.get("Tags", {}).get("Items", [])]

def get_cloudfront_config(distribution_id):
    try:
        dist = cloudfront.get_distribution(Id=distribution_id)["Distribution"]
        config = dist["DistributionConfig"]

        tags = cloudfront.list_tags_for_resource(
            Resource=f"arn:aws:cloudfront::{dist['ARN'].split(':')[4]}:distribution/{distribution_id}"
        )

        return {
            "id": distribution_id,
            "arn": dist["ARN"],
            "domain_name": dist["DomainName"],
            "status": dist["Status"],
            "enabled": config.get("Enabled", True),
            "price_class": config.get("PriceClass"),
            "is_ipv6_enabled": config.get("IsIPV6Enabled", False),
            "http_version": config.get("HttpVersion"),
            "comment": config.get("Comment", ""),
            "default_root_object": config.get("DefaultRootObject"),
            "tags": format_tags(tags),
            "origins": [
                {
                    "id": origin["Id"],
                    "domain_name": origin["DomainName"],
                    "origin_path": origin.get("OriginPath", ""),
                    "custom_headers": origin.get("CustomHeaders", {}).get("Items", []),
                    "s3_origin_config": origin.get("S3OriginConfig"),
                    "custom_origin_config": origin.get("CustomOriginConfig"),
                }
                for origin in config["Origins"].get("Items", [])
            ],
            "default_cache_behavior": config.get("DefaultCacheBehavior", {}),
            "cache_behaviors": [
                {
                    "path_pattern": item["PathPattern"],
                    "target_origin_id": item["TargetOriginId"],
                    "viewer_protocol_policy": item["ViewerProtocolPolicy"],
                    "allowed_methods": item.get("AllowedMethods"),
                    "cached_methods": item.get("CachedMethods"),
                    "forwarded_values": item.get("ForwardedValues"),
                    "min_ttl": item.get("MinTTL"),
                    "default_ttl": item.get("DefaultTTL"),
                    "max_ttl": item.get("MaxTTL"),
                }
                for item in config.get("CacheBehaviors", {}).get("Items", [])
            ],
            "viewer_certificate": config.get("ViewerCertificate", {}),
            "restrictions": config.get("Restrictions", {}),
            "aliases": config.get("Aliases", {}).get("Items", []),
            "logging": config.get("Logging", {}),
            "web_acl_id": config.get("WebACLId", ""),
        }

    except Exception as e:
        print(f"⚠️ Failed to get CloudFront distribution {distribution_id}: {e}")
        return None
