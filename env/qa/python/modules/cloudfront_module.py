# modules/cloudfront_module.py

import boto3

cloudfront = boto3.client("cloudfront")

def format_tags(tag_response):
    """Convert AWS tag response to Terraform map format."""
    return {tag["Key"]: tag["Value"] for tag in tag_response.get("Tags", {}).get("Items", [])}

def list_all_distributions():
    """List all CloudFront distributions."""
    try:
        dist_ids = []
        paginator = cloudfront.get_paginator("list_distributions")
        for page in paginator.paginate():
            for dist in page.get("DistributionList", {}).get("Items", []):
                dist_ids.append(dist["Id"])
        return dist_ids
    except Exception as e:
        print(f"WARNING Failed to list CloudFront distributions: {e}")
        return []

def get_cloudfront_config(distribution_id):
    try:
        dist = cloudfront.get_distribution(Id=distribution_id)["Distribution"]
        config = dist["DistributionConfig"]

        tags = cloudfront.list_tags_for_resource(
            Resource=f"arn:aws:cloudfront::{dist['ARN'].split(':')[4]}:distribution/{distribution_id}"
        )

        # Process origins
        tf_origins = []
        for origin in config["Origins"].get("Items", []):
            origin_dict = {
                "origin_id": origin["Id"],
                "domain_name": origin["DomainName"],
            }
            if origin.get("OriginPath"):
                origin_dict["origin_path"] = origin["OriginPath"]
            
            # Custom headers
            if origin.get("CustomHeaders", {}).get("Items"):
                origin_dict["custom_headers"] = [
                    {"name": h["HeaderName"], "value": h["HeaderValue"]}
                    for h in origin["CustomHeaders"]["Items"]
                ]
            
            # S3 origin config
            if origin.get("S3OriginConfig"):
                origin_dict["s3_origin_config"] = {
                    "origin_access_identity": origin["S3OriginConfig"].get("OriginAccessIdentity")
                }
            
            # Custom origin config
            if origin.get("CustomOriginConfig"):
                cog = origin["CustomOriginConfig"]
                origin_dict["custom_origin_config"] = {
                    "http_port": cog.get("HTTPPort", 80),
                    "https_port": cog.get("HTTPSPort", 443),
                    "origin_protocol_policy": cog.get("OriginProtocolPolicy", "http-only"),
                    "origin_ssl_protocols": cog.get("OriginSslProtocols", {}).get("Items", ["TLSv1.2"])
                }
                if cog.get("OriginKeepaliveTimeout"):
                    origin_dict["custom_origin_config"]["origin_keepalive_timeout"] = cog["OriginKeepaliveTimeout"]
                if cog.get("OriginReadTimeout"):
                    origin_dict["custom_origin_config"]["origin_read_timeout"] = cog["OriginReadTimeout"]
            
            tf_origins.append(origin_dict)

        # Process default cache behavior
        dcb = config.get("DefaultCacheBehavior", {})
        tf_dcb = {
            "target_origin_id": dcb.get("TargetOriginId"),
            "viewer_protocol_policy": dcb.get("ViewerProtocolPolicy", "allow-all"),
            "allowed_methods": dcb.get("AllowedMethods", {}).get("Items", ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]),
            "cached_methods": dcb.get("CachedMethods", {}).get("Items", ["GET", "HEAD"]),
            "compress": dcb.get("Compress", False),
            "min_ttl": dcb.get("MinTTL", 0),
            "default_ttl": dcb.get("DefaultTTL", 86400),
            "max_ttl": dcb.get("MaxTTL", 31536000),
            "forwarded_values": {
                "query_string": dcb.get("ForwardedValues", {}).get("QueryString", False),
                "headers": dcb.get("ForwardedValues", {}).get("Headers", {}).get("Items", []),
                "cookies": {
                    "forward": dcb.get("ForwardedValues", {}).get("Cookies", {}).get("Forward", "none")
                }
            }
        }

        # Process cache behaviors
        tf_cache_behaviors = []
        for cb in config.get("CacheBehaviors", {}).get("Items", []):
            tf_cb = {
                "path_pattern": cb.get("PathPattern"),
                "target_origin_id": cb.get("TargetOriginId"),
                "viewer_protocol_policy": cb.get("ViewerProtocolPolicy", "allow-all"),
                "allowed_methods": cb.get("AllowedMethods", {}).get("Items", ["GET", "HEAD"]),
                "cached_methods": cb.get("CachedMethods", {}).get("Items", ["GET", "HEAD"]),
                "compress": cb.get("Compress", False),
                "min_ttl": cb.get("MinTTL", 0),
                "default_ttl": cb.get("DefaultTTL", 86400),
                "max_ttl": cb.get("MaxTTL", 31536000),
                "forwarded_values": {
                    "query_string": cb.get("ForwardedValues", {}).get("QueryString", False),
                    "headers": cb.get("ForwardedValues", {}).get("Headers", {}).get("Items", []),
                    "cookies": {
                        "forward": cb.get("ForwardedValues", {}).get("Cookies", {}).get("Forward", "none")
                    }
                }
            }
            tf_cache_behaviors.append(tf_cb)

        # Process viewer certificate
        vc = config.get("ViewerCertificate", {})
        tf_viewer_cert = {}
        if vc.get("CloudFrontDefaultCertificate"):
            tf_viewer_cert["cloudfront_default_certificate"] = True
        if vc.get("IAMCertificateId"):
            tf_viewer_cert["iam_certificate_id"] = vc["IAMCertificateId"]
        if vc.get("ACMCertificateArn"):
            tf_viewer_cert["acm_certificate_arn"] = vc["ACMCertificateArn"]
        if vc.get("SSLSupportMethod"):
            tf_viewer_cert["ssl_support_method"] = vc["SSLSupportMethod"]
        if vc.get("MinimumProtocolVersion"):
            tf_viewer_cert["minimum_protocol_version"] = vc["MinimumProtocolVersion"]

        # Process restrictions
        tf_restrictions = {}
        if config.get("Restrictions"):
            geo = config["Restrictions"].get("GeoRestriction", {})
            if geo:
                tf_restrictions["geo_restriction"] = {
                    "restriction_type": geo.get("RestrictionType", "none"),
                    "locations": geo.get("Locations", [])
                }

        # Process logging
        tf_logging = {}
        if config.get("Logging"):
            lg = config["Logging"]
            tf_logging = {
                "bucket": lg.get("Bucket"),
                "include_cookies": lg.get("IncludeCookies", False)
            }
            if lg.get("Prefix"):
                tf_logging["prefix"] = lg["Prefix"]

        return {
            "enabled": config.get("Enabled", True),
            "is_ipv6_enabled": config.get("IsIPV6Enabled", False),
            "comment": config.get("Comment", ""),
            "default_root_object": config.get("DefaultRootObject"),
            "price_class": config.get("PriceClass"),
            "http_version": config.get("HttpVersion"),
            "web_acl_id": config.get("WebACLId"),
            "origins": tf_origins,
            "default_cache_behavior": tf_dcb,
            "cache_behaviors": tf_cache_behaviors if tf_cache_behaviors else None,
            "viewer_certificate": tf_viewer_cert if tf_viewer_cert else None,
            "restrictions": tf_restrictions if tf_restrictions else None,
            "aliases": config.get("Aliases", {}).get("Items", []),
            "logging": tf_logging if tf_logging else None,
            "tags": format_tags(tags),
        }

    except Exception as e:
        print(f"WARNING Failed to get CloudFront distribution {distribution_id}: {e}")
        return None
