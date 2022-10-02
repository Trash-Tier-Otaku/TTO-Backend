import os
import boto3
from dotenv import load_dotenv 

load_dotenv()

IS_OFFLINE = os.getenv('IS_OFFLINE')

if IS_OFFLINE:
    DYNAMO_CLIENT = boto3.client(
        'dynamodb',
        region_name='localhost',
        endpoint_url='http://localhost:8000'
    )
else:
    DYNAMO_CLIENT = boto3.client('dynamodb') 

LOGIN_TABLE = os.getenv('LOGIN_TABLE')
USER_TABLE = os.getenv('USER_TABLE')

MAL_API_ID = os.getenv('MAL_API_ID')
MAL_API_SECRET = os.getenv('MAL_API_SECRET')