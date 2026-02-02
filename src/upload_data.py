import boto3

s3 = boto3.client(
    's3', 
    endpoint_url="http://localhost:4566",
    aws_access_key_id="test",
    aws_secret_access_key="test",
    region_name="us-east-1"
)

# uploading local data file to s3
try:
    s3.upload_file("data/raw/bike_sharing_raw.csv", "bike-sharing", "raw.csv")
    print("Success: Data uploaded to S3 bucket!")
except Exception as e:
    print(f"Error: {e}")