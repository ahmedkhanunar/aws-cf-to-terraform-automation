import boto3

# Initialize EC2 client
ec2 = boto3.client("ec2", region_name="us-east-1")  # Make sure region is correct

vpc_id = "vpc-014c0cbc184161054"

try:
    # Describe NAT Gateways
    # Fetch NAT Gateways (with additional debugging)
    try:
        nat_gateways = ec2.describe_nat_gateways(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])["NatGateways"]
    except KeyError:
        print(f"⚠️ No NAT Gateways found for VPC {vpc_id}.")
        nat_gateways = []
    
    # Initialize vpc_block as a dictionary
    vpc_block = {
        "nat_gateways": []  # Initialize the nat_gateways key as an empty list
    }

    # Process NAT Gateways
    if nat_gateways:
        for nat in nat_gateways:
            vpc_block["nat_gateways"].append({
                "nat_gateway_id": nat["NatGatewayId"],
                "subnet_id": nat["SubnetId"],
                "state": nat["State"],
                "elastic_ip": nat.get("NatGatewayAddresses", [{}])[0].get("PublicIp"),
            })
        print("NAT Gateways found:", vpc_block["nat_gateways"])
    else:
        print("No NAT Gateways found for VPC:", vpc_id)

except Exception as e:
    print(f"Failed to retrieve NAT Gateways for VPC {vpc_id}: {e}")
