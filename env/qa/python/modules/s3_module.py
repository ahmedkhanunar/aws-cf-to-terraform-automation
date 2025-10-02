import boto3
from botocore.exceptions import ClientError

s3 = boto3.client("s3")

# -----------------------
# Function: Get S3 bucket config
# -----------------------
def get_s3_config(bucket_name):
    try:
        # Region
        region = s3.get_bucket_location(Bucket=bucket_name)["LocationConstraint"]
        if region is None:  # us-east-1 special case
            region = "us-east-1"

        # Creation date
        creation_date = None
        for b in s3.list_buckets()["Buckets"]:
            if b["Name"] == bucket_name:
                creation_date = b["CreationDate"].isoformat()
                break

        # Versioning
        versioning = s3.get_bucket_versioning(Bucket=bucket_name)
        versioning_status = versioning.get("Status", "Disabled")

        return {
            "bucket": bucket_name,
            "region": region,
            "creation_date": creation_date,
            "versioning_status": versioning_status,
        }
    except Exception as e:
        print(f"⚠️ Error fetching bucket {bucket_name}: {e}")
        return None


