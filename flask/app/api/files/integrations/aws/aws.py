import boto3, botocore
from botocore.config import Config
import json

from app.api.files.integrations.aws.exceptions import *


def get_s3_client():
    # AWS authentication is made using env variables:
    # AWS_ACCESS_KEY_ID: The access key for the AWS account.
    # AWS_SECRET_ACCESS_KEY: The secret key for the AWS account.
    my_config = Config(
        region_name="eu-west-1",
        signature_version="v4",
        retries={"max_attempts": 10, "mode": "standard"},
    )
    return boto3.client("s3", config=my_config)


def list_buckets(s3_client):
    return s3_client.list_buckets()


def bucket_exists(s3_client, bucket_name):
    """Returns whether the given s3_client has access to the specified bucket"""
    try:
        resp = s3_client.head_bucket(Bucket=bucket_name)
        print(resp, flush=True)
        return True
    except botocore.exceptions.NoCredentialsError as e:
        raise e
    except botocore.exceptions.ClientError as e:
        error_code = int(e.response["Error"]["Code"])
        print(e, flush=True)
        if error_code == 404 or error_code == 403:
            return False
        else:
            print(e.response, flush=True)
            raise e


def create_bucket(s3_client, bucket_name):
    try:
        response = s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint": "eu-west-1"},
        )

        print(response, flush=True)
        # TODO: get Principal arn programmatically

        bucket_arn = f"arn:aws:s3:::{bucket_name}/*"
        policy_payload = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "Allow Public Access to All Objects",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": bucket_arn,
                },
                {
                    "Sid": "allow account to put objects",
                    "Effect": "Allow",
                    "Principal": {"AWS": "arn:aws:iam::212334386917:user/s3-rw"},
                    "Action": [
                        "s3:PutObject",
                        "s3:PutObjectAcl",
                        "s3:PutObjectTagging",
                    ],
                    "Resource": bucket_arn,
                },
            ],
        }
        s3_client.put_bucket_policy(
            Bucket=bucket_name, Policy=json.dumps(policy_payload)
        )
        # bucket_policy.put(Policy=json.dumps(policy_payload))

    except botocore.exceptions.ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "InvalidBucketName":
            raise AWSInvalidBucketNameException(
                f"Given bucket name is invalid: {bucket_name}"
            )
        elif error_code == "BucketAlreadyOwnedByYou":
            raise AWSBucketAlreadyExistsException(
                description=e.response["Error"]["Message"]
            )
        else:
            print(e.response, flush=True)
            raise e


def delete_bucket(s3_client, bucket_name):
    try:
        s3_client.delete_bucket(Bucket=bucket_name)
    except botocore.exceptions.ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "NoSuchBucket":
            raise AWSNotFoundException(e.response["Error"]["Message"])
        elif error_code == "BucketNotEmpty":
            raise AWSForbiddenException("Could not delete bucket: Forbidden")
        else:
            print(e.response, flush=True)
            raise e


def upload_file(s3_client, bucket_name, file_name, file, mime_type):
    try:
        response = s3_client.upload_fileobj(
            file, bucket_name, file_name, ExtraArgs={"ContentType": mime_type}
        )
    except botocore.exceptions.ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "NoSuchBucket":
            raise AWSNotFoundException(description=e.response["Error"]["Message"])
        else:
            print(e.response, flush=True)
            raise e


def get_all_files(s3_client, bucket_name):
    try:
        response = s3_client.list_objects(
            Bucket=bucket_name,
            EncodingType="url",
        )
        print(response, flush=True)
        # The AWS API does not return Contents if there exists no file
        return response.get("Contents", [])
    except botocore.exceptions.ClientError as e:
        print(e.response, flush=True)
        raise e


def delete_file(s3_client, bucket_name, file_name):
    try:
        response = s3_client.delete_object(
            Bucket=bucket_name,
            Key=file_name,
        )
        print(response, flush=True)
    except botocore.exceptions.ClientError as e:
        print(e.response, flush=True)
        raise e


def get_file_url(s3_client, bucket_name, file_name):
    full_url = s3_client.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": bucket_name, "Key": file_name},
    )
    return full_url.split("?")[0]
