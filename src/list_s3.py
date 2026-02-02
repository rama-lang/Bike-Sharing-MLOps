import boto3

s3 = boto3.client(
    's3', 
    endpoint_url="http://localhost:4566",
    aws_access_key_id="test",
    aws_secret_access_key="test",
    region_name="us-east-1"
)

print("--- Checking S3 Buckets ---")
buckets = s3.list_buckets()
for bucket in buckets['Buckets']:
    print(f"Bucket: {bucket['Name']}")
    
    # checking files in the bucket
    try:
        objs = s3.list_objects_v2(Bucket=bucket['Name'])
        if 'Contents' in objs:
            for obj in objs['Contents']:
                print(f"  - File found: {obj['Key']}")
        else:
            print("  - (Bucket is empty)")
    except Exception as e:
        print(f"  - Error listing files: {e}")