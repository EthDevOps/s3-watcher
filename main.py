import boto3
from datetime import datetime, timedelta, timezone
import requests
import sys
import os

def check_recent_files(s3_endpoint, s3_bucket, s3_access_key, s3_secret_key, grace_period, s3_folder):
    # Initialize a session using your credentials
    s3 = boto3.client(
            's3',
            endpoint_url=s3_endpoint,
            aws_access_key_id=s3_access_key,
            aws_secret_access_key=s3_secret_key,
            region_name='us-east-1',
            config=boto3.session.Config(signature_version='s3v4')  # Use S3v4 signature
            )
    
    # Calculate the time 12 hours ago
    twelve_hours_ago = datetime.now(timezone.utc) - timedelta(hours=grace_period)
    
    # List objects in the specified S3 bucket
    response = s3.list_objects_v2(Bucket=s3_bucket, Prefix=s3_folder)
    
    # Check if 'Contents' key is in the response (it's not present if the bucket is empty)
    if 'Contents' in response:
        for obj in response['Contents']:
            # Get the last modified time of the file
            last_modified = obj['LastModified']
            
            # Check if the file was modified within the last 12 hours

            if last_modified > twelve_hours_ago:
                print(f"File found: {obj['Key']} modified at {last_modified}")
                return True

    # If no recent file is found, send a GET request to the health check URL
    print("No recent files found.")
    return False

def get_env(var_name):
    """Retrieve required environment variable or raise an exception."""
    try:
        return os.environ[var_name]
    except KeyError:
        raise EnvironmentError(f"Required environment variable '{var_name}' not set.")

if __name__ == '__main__':
    # Specify your bucket name here

    # Get env names
    s3_endpoint = get_env("S3_ENDPOINT")
    s3_bucket = get_env("S3_BUCKET")
    s3_folder = get_env("S3_FOLDER")
    s3_access_key = get_env("S3_ACCESS_KEY")
    s3_secret_key = get_env("S3_SECRET_KEY")
    healthcheck_url = get_env("HEALTHCHECK_URL")
    grace_period = int(get_env("GRACE_PERIOD"))

    has_recent_files = check_recent_files(s3_endpoint, s3_bucket, s3_access_key, s3_secret_key, grace_period, s3_folder)

    # Notify a successful ping
    if has_recent_files:
        print("File found - sending ping")
        requests.get(healthcheck_url)
