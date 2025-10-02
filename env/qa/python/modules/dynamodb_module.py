import boto3
dynamodb = boto3.client("dynamodb")

# -----------------------
# Function: Get DynamoDB table config
# -----------------------
def get_dynamodb_config(table_name):
    try:
        desc = dynamodb.describe_table(TableName=table_name)["Table"]
        return {
            "table_name": desc["TableName"],
            "region": dynamodb.meta.region_name,
            "status": desc["TableStatus"],
            "billing_mode": desc.get("BillingModeSummary", {}).get("BillingMode", "PROVISIONED"),
            "read_capacity": desc.get("ProvisionedThroughput", {}).get("ReadCapacityUnits"),
            "write_capacity": desc.get("ProvisionedThroughput", {}).get("WriteCapacityUnits"),
            "key_schema": desc["KeySchema"],
            "attributes": desc["AttributeDefinitions"],
        }
    except Exception as e:
        print(f"⚠️ Error fetching DynamoDB table {table_name}: {e}")
        return None
