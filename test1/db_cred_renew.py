import boto3
import redis
import json
from botocore.exceptions import ClientError
from datetime import timedelta


def get_secret():
    secret_name = "rds!db-dc5b79b1-85c4-4e78-b0af-fa5361bcbad3"
    region_name = "us-west-2"

    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)

    try:
        response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        raise RuntimeError(f"Failed to fetch secret: {e}")

    return json.loads(response['SecretString'])


def store_secret_in_redis(secret_data):
    # Connect to Redis (adjust host and port as needed)
    r = redis.Redis(host='localhost', port=6379, db=0)

    # Store as a JSON string
    r.set("db_credentials", json.dumps(secret_data))

    # Optionally set an expiry
    r.expire("db_credentials", timedelta(days=7).seconds)

    print("Credentials updated in Redis.")


def get_db_credentials():
    r = redis.Redis(host='localhost', port=6379, db=0)
    credentials = r.get("db_credentials")

    if not credentials:
        raise ValueError("Database credentials not found in Redis.")

    return json.loads(credentials)


if __name__ == "__main__":
    secret = get_secret()
    store_secret_in_redis(secret)
