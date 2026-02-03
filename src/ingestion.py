import boto3
import pandas as pd
import yaml
import os

CONFIG_PATH = os.path.join("/opt/airflow/src", "config.yaml")

def load_data():

    if not os.path.exists(CONFIG_PATH):
        print(f"Error: {CONFIG_PATH} file not found!")
        return None

    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)

    try:
        s3 = boto3.client(
            's3',
            endpoint_url=config['aws']['endpoint_url'],
            aws_access_key_id="test",
            aws_secret_access_key="test",
            region_name=config['aws']['region_name']
        )

        bucket_name = config['aws']['bucket_name']
        file_key = config['aws']['raw_file_key']
        local_path = config['data']['raw_path']

        
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

       
        print(f"Connecting to LocalStack at {config['aws']['endpoint_url']}...")
        print(f"Downloading {file_key} from bucket: {bucket_name}...")
        
        s3.download_file(bucket_name, file_key, local_path)
        print(f"Success! File saved to: {local_path}")

       
        df = pd.read_csv(local_path)
        print(f"Total records loaded: {df.shape[0]}")
        return df

    except Exception as e:
        print(f"Error occurred during data ingestion: {e}")
        return None

if __name__ == "__main__":
    load_data()