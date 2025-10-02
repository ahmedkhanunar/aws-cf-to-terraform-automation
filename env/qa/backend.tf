terraform {
  backend "s3" {
    bucket         = "porter-qa-ops-terraform"       # S3 bucket name
    key            = "envs/qa/terraform.tfstate" # Path within the bucket
    region         = "us-east-1"                 # Bucket region
    encrypt        = true                        # Encrypt state at rest
    # dynamodb_table = "terraform-locks"           # Optional: for state locking
  }
}