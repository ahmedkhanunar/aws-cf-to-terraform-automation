import boto3

ec2 = boto3.client("ec2")

def format_tags(tag_list):
    """Convert AWS tag list to Terraform-style list of maps."""
    return [{"Key": tag["Key"], "Value": tag["Value"]} for tag in tag_list]

def get_vpc_config(vpc_id):
    try:
        # Fetch VPC and associated resources
        vpc_response = ec2.describe_vpcs(VpcIds=[vpc_id])["Vpcs"][0]
        subnets = ec2.describe_subnets(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])["Subnets"]
        igws = ec2.describe_internet_gateways(Filters=[{"Name": "attachment.vpc-id", "Values": [vpc_id]}])["InternetGateways"]
        route_tables = ec2.describe_route_tables(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])["RouteTables"]
        security_groups = ec2.describe_security_groups(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])["SecurityGroups"]
        nacls = ec2.describe_network_acls(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])["NetworkAcls"]

        # Filter out the default Network ACLs (IsDefault is True)
        nacls = [nacl for nacl in nacls if not nacl["IsDefault"]]

        # Fetch NAT Gateways (with additional debugging)
        try:
            nat_gateways = ec2.describe_nat_gateways(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])["NatGateways"]
        except KeyError:
            print(f"⚠️ No NAT Gateways found for VPC {vpc_id}.")
            nat_gateways = []

        # Fetch Elastic IPs
        eips = ec2.describe_addresses(Filters=[{"Name": "domain", "Values": ["vpc"]}])["Addresses"]

        # Build the VPC object for Terraform
        vpc_block = {
            "cidr_block": vpc_response["CidrBlock"],
            "instance_tenancy": vpc_response.get("InstanceTenancy", "default"),
            "enable_dns_support": True,
            "enable_dns_hostnames": True,
            "tags": format_tags(vpc_response.get("Tags", [])),
            "subnets": [],
            "nat_gateways": [],  # Initialize nat_gateways key
            "eips": [],           # Initialize eips key
        }

        # Add Subnets (Terraform expects a list inside the VPC object)
        for subnet in subnets:
            vpc_block["subnets"].append({
                "subnet_id": subnet["SubnetId"],
                "cidr_block": subnet["CidrBlock"],
                "availability_zone": subnet.get("AvailabilityZone"),
                "availability_zone_id": subnet.get("AvailabilityZoneId"),
                "map_public_ip_on_launch": subnet.get("MapPublicIpOnLaunch", False),
                "tags": format_tags(subnet.get("Tags", [])),
            })

        # Process NAT Gateways
        if nat_gateways:
            for nat in nat_gateways:
                vpc_block["nat_gateways"].append({
                    "nat_gateway_id": nat["NatGatewayId"],
                    "subnet_id": nat["SubnetId"],
                    "state": nat["State"],
                    "elastic_ip": nat.get("NatGatewayAddresses", [{}])[0].get("PublicIp"),
                    "tags": format_tags(nat.get("Tags", [])),
                })
        else:
            print(f"No NAT Gateways found for VPC {vpc_id}.")

        # Process Elastic IPs (EIPs)
        for eip in eips:
            vpc_block["eips"].append({
                "allocation_id": eip["AllocationId"],
                "public_ip": eip["PublicIp"],
                "association_id": eip.get("AssociationId"),
                "tags": format_tags(eip.get("Tags", [])),
            })
        
        # Process security groups
        sg_data = {}
        for sg in security_groups:
            sg_id = sg["GroupId"]
            sg_data[sg_id] = {
                "group_name": sg["GroupName"],
                "description": sg["Description"],
                "vpc_id": sg["VpcId"],
                "tags": format_tags(sg.get("Tags", [])),
                "ingress_rules": [],
                "egress_rules": [],
            }

            # Process Ingress Rules
            for rule in sg.get("IpPermissions", []):
                # Handle missing FromPort and ToPort
                ingress_rule = {
                    "ip_protocol": rule.get("IpProtocol"),
                    "from_port": rule.get("FromPort", None),  # None if missing
                    "to_port": rule.get("ToPort", None),  # None if missing
                    "cidr_blocks": [ip["CidrIp"] for ip in rule.get("IpRanges", [])],
                    "ipv6_cidr_blocks": [ip.get("CidrIpv6") for ip in rule.get("Ipv6Ranges", [])],
                    "prefix_list_ids": rule.get("PrefixListIds", []),
                    "user_group_pairs": rule.get("UserIdGroupPairs", []),
                }
                sg_data[sg_id]["ingress_rules"].append(ingress_rule)

            # Process Egress Rules
            for rule in sg.get("IpPermissionsEgress", []):
                # Handle missing FromPort and ToPort
                egress_rule = {
                    "ip_protocol": rule.get("IpProtocol"),
                    "from_port": rule.get("FromPort", None),  # None if missing
                    "to_port": rule.get("ToPort", None),  # None if missing
                    "cidr_blocks": [ip["CidrIp"] for ip in rule.get("IpRanges", [])],
                    "ipv6_cidr_blocks": [ip.get("CidrIpv6") for ip in rule.get("Ipv6Ranges", [])],
                    "prefix_list_ids": rule.get("PrefixListIds", []),
                    "user_group_pairs": rule.get("UserIdGroupPairs", []),
                }
                sg_data[sg_id]["egress_rules"].append(egress_rule)


        return {
            "vpc": vpc_block,
            "internet_gateways": igws,
            "route_tables": route_tables,
            "security_groups": sg_data,  # Include the processed security group data
            "network_acls": nacls,  # Now, this list excludes default ACLs
            "nat_gateways": vpc_block["nat_gateways"],
            "eips": vpc_block["eips"],
        }

    except Exception as e:
        print(f"⚠️ Failed to get VPC {vpc_id}: {e}")
        return None


def extract_flat_resources(data):
    """Flatten nested data for separate Terraform modules."""
    result = {
        "vpcs": {},
        "subnets": {},
        "internet_gateways": {},
        "route_tables": {},
        "security_groups": {},
        "network_acls": {},
        "nat_gateways": {},
        "eips": {}
    }

    for vpc_id, config in data.get("vpcs", {}).items():
        if not isinstance(config, dict):
            continue

        vpc_block = config.get("vpc")
        if vpc_block:
            result["vpcs"][vpc_id] = vpc_block

            # Flatten subnets from inside the VPC block
            for subnet in vpc_block.get("subnets", []):
                subnet_id = subnet.get("subnet_id")
                if subnet_id:
                    result["subnets"][subnet_id] = {**subnet, "vpc_id": vpc_id}

        for igw in config.get("internet_gateways", []):
            igw_id = igw.get("InternetGatewayId")
            if igw_id:
                result["internet_gateways"][igw_id] = igw

        for rtb in config.get("route_tables", []):
            rtb_id = rtb.get("RouteTableId")
            if rtb_id:
                result["route_tables"][rtb_id] = rtb

        for sg_id, sg in config.get("security_groups", {}).items():
            if isinstance(sg, dict):  # Ensure it's a dictionary
                result["security_groups"][sg_id] = sg

        for nacl in config.get("network_acls", []):
            nacl_id = nacl.get("NetworkAclId")
            if nacl_id:
                result["network_acls"][nacl_id] = nacl

        # Add NAT Gateways to the result
        for nat in config.get("nat_gateways", []):
            nat_id = nat.get("nat_gateway_id")
            if nat_id:
                result["nat_gateways"][nat_id] = nat

        # Add EIPs to the result
        for eip in config.get("eips", []):
            eip_id = eip.get("allocation_id")
            if eip_id:
                result["eips"][eip_id] = eip
        
    return result
