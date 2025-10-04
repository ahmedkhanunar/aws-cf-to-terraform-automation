import boto3

wafv2 = boto3.client("wafv2")

# Helper to detect the scope from ARN
def detect_scope_from_arn(arn: str) -> str:
    if ":global/" in arn:
        return "CLOUDFRONT"
    return "REGIONAL"

# Function to get WebACL config, extended to call IP Set info
def get_web_acl_config(rid: str):
    try:
        # Case 1: If rid is in ARN format
        if rid.startswith("arn:aws:wafv2:"):
            scope = detect_scope_from_arn(rid)
            name = rid.split("/")[-1]
            id_ = rid.split("/")[-2]
        
        # Case 2: If rid is in the form Name|Id|Scope
        elif "|" in rid:
            parts = rid.split("|")
            if len(parts) != 3:
                raise ValueError(f"Invalid WAF WebACL ID format: {rid}")
            name, id_, scope = parts
        else:
            raise ValueError(f"Unsupported WAF WebACL rid format: {rid}")

        # Fetch WebACL configuration from WAF
        resp = wafv2.get_web_acl(Name=name, Scope=scope, Id=id_)
        web_acl = resp.get("WebACL", {})

        # Get tags using the correct parameter name (ResourceARN)
        tags_resp = wafv2.list_tags_for_resource(ResourceARN=web_acl.get("ARN"))
        tags = tags_resp.get("TagList", {})

        # Find IP Sets from rules
        ip_sets = []
        for rule in web_acl.get("Rules", []):
            # Check if the rule contains an IPSetReferenceStatement
            if "Statement" in rule and "IPSetReferenceStatement" in rule["Statement"]:
                ip_set_id = rule["Statement"]["IPSetReferenceStatement"].get("ARN")
                if ip_set_id:
                    # Call get_ip_set_config for the IP Set ARN
                    ip_set_config = get_ip_set_config(ip_set_id)
                    ip_sets.append(ip_set_config)

        return {
            "name": web_acl.get("Name", ""),
            "id": web_acl.get("Id", ""),
            "arn": web_acl.get("ARN", ""),
            "scope": scope,
            "description": web_acl.get("Description", ""),
            "visibility_config": web_acl.get("VisibilityConfig", {}),
            "tags": tags,
            "ip_sets": ip_sets,  # Added list of IP Sets
        }
    except Exception as e:
        print(f"⚠️ Failed to fetch WAF WebACL {rid}: {e}")
        return None

# Function to get IP Set config
def get_ip_set_config(rid: str):
    try:
        # Case 1: If rid is in ARN format
        if rid.startswith("arn:aws:wafv2:"):
            scope = detect_scope_from_arn(rid)
            name = rid.split("/")[-1]
            id_ = rid.split("/")[-2]

        # Case 2: If rid is in the form Name|Id|Scope
        elif "|" in rid:
            parts = rid.split("|")
            if len(parts) != 3:
                raise ValueError(f"Invalid WAF IPSet ID format: {rid}")
            name, id_, scope = parts
        else:
            raise ValueError(f"Unsupported WAF IPSet rid format: {rid}")

        # Fetch IP Set configuration from WAF
        resp = wafv2.get_ip_set(Name=name, Scope=scope, Id=id_)
        ip_set = resp.get("IPSet", {})

        # Get tags using the correct parameter name (ResourceARN)
        tags_resp = wafv2.list_tags_for_resource(ResourceARN=ip_set.get("ARN"))
        tags = tags_resp.get("TagList", {})

        return {
            "name": ip_set.get("Name", ""),
            "id": ip_set.get("Id", ""),
            "arn": ip_set.get("ARN", ""),
            "scope": scope,
            "description": ip_set.get("Description", ""),
            "ip_address_version": ip_set.get("IPAddressVersion", ""),
            "addresses": ip_set.get("Addresses", []),
            "tags": tags,
        }
    except Exception as e:
        print(f"⚠️ Failed to fetch WAF IPSet {rid}: {e}")
        return None
