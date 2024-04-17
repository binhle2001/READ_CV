from api.helpers.common import get_env_var
import boto3

s3 = boto3.client(
    's3',
    aws_access_key_id = get_env_var('s3', 'AWS_ACCESS_KEY_ID'),
    aws_secret_access_key = get_env_var('s3', 'AWS_SECRET_ACCESS_KEY'),
    region_name = get_env_var('s3', 'AWS_REGION_NAME'),
)