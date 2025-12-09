import boto3
from botocore.exceptions import ClientError
from boto3.s3.transfer import TransferConfig

# --- CONFIGURATION ---
AWS_REGION = "us-west-2"
BUCKET_NAME = "bastian-lab-169-3-r-us-west-2.sec.ucsf.edu"
DRY_RUN = False  # ✅ Set to False after confirming output
PREFIX = ""     # e.g., "HiSeqData/" if you want to limit scope

CONFIG = TransferConfig(
    multipart_threshold=8 * 1024 * 1024,
    multipart_chunksize=64 * 1024 * 1024,
    max_concurrency=10,
    use_threads=True
)

from botocore.exceptions import ClientError

def safe_head_object(client, bucket, key):
    try:
        return client.head_object(Bucket=bucket, Key=key)
    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code in ("404", "NoSuchKey", "NotFound"):
            print(f"⚠️ Object not found or already archived: {key}")
            return None
        else:
            raise
def convert_glacier_and_mark_level():
    s3 = boto3.resource("s3", region_name=AWS_REGION)
    client = s3.meta.client

    continuation_token = None
    total = changed = skipped = errors = 0

    while True:
        list_kwargs = {"Bucket": BUCKET_NAME, "MaxKeys": 1000}
        if PREFIX:
            list_kwargs["Prefix"] = PREFIX
        if continuation_token:
            list_kwargs["ContinuationToken"] = continuation_token

        response = client.list_objects_v2(**list_kwargs)
        if "Contents" not in response:
            break

        for obj in response["Contents"]:
            key = obj["Key"]
            size = obj["Size"]
            total += 1
            print(total)

            # --- 🧩 Skip AWS-managed and mirror delivery log files ---
            if key.startswith(("managed-", "mmdl-")):
                skipped += 1
                continue

            # --- Skip folder markers and zero-byte objects ---
            if key.endswith("/") or size == 0:
                skipped += 1
                continue

            head = safe_head_object(client, BUCKET_NAME, key)
            if not head:
                errors += 1
                continue

            storage_class = head.get("StorageClass", "STANDARD")
            if storage_class in ("GLACIER", "GLACIER_IR", "DEEP_ARCHIVE"):
                skipped += 1
                continue

            copy_source = {"Bucket": BUCKET_NAME, "Key": key}
            extra_args = {"StorageClass": "DEEP_ARCHIVE", "MetadataDirective": "COPY"}

            try:
                s3.Object(BUCKET_NAME, key).copy(
                    copy_source, ExtraArgs=extra_args, Config=CONFIG
                )
                changed += 1
                print(f"✅ Converted {key} → DEEP_ARCHIVE")
            except ClientError as e:
                errors += 1
                print(f"❌ Copy failed for {key}: {e}")

        if response.get("IsTruncated"):
            continuation_token = response["NextContinuationToken"]
        else:
            break

    print(f"\n📊 Summary for {BUCKET_NAME}")
    print(f"  Total scanned : {total}")
    print(f"  Converted     : {changed}")
    print(f"  Skipped       : {skipped}")
    print(f"  Errors        : {errors}")


import boto3
from botocore.exceptions import ClientError
from boto3.s3.transfer import TransferConfig

# --- CONFIGURATION ---
AWS_REGION = "us-west-2"
BUCKET_NAME = "bastian-lab-169-3-r-us-west-2.sec.ucsf.edu"
DRY_RUN = False  # Set to True to see actions without changing S3
PREFIX = "BastianRaid-02/HiSeqData/BCB119_NC12685/NC12685/AM2-062/"

CONFIG = TransferConfig(
    multipart_threshold=8 * 1024 * 1024,
    multipart_chunksize=64 * 1024 * 1024,
    max_concurrency=10,
    use_threads=True
)

s3 = boto3.client("s3", region_name=AWS_REGION)

def convert_to_standard():
    try:
        paginator = s3.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=BUCKET_NAME, Prefix=PREFIX)

        for page in pages:
            if "Contents" not in page:
                continue

            for obj in page["Contents"]:
                key = obj["Key"]

                print(f"Processing: {key}")

                if DRY_RUN:
                    print(f"DRY RUN: Would copy {key} to STANDARD")
                    continue

                # Copy object to itself with STANDARD storage class
                try:
                    s3.copy_object(
                        Bucket=BUCKET_NAME,
                        CopySource={"Bucket": BUCKET_NAME, "Key": key},
                        Key=key,
                        StorageClass="STANDARD",
                        MetadataDirective="COPY"
                    )
                    print(f"✓ Converted to STANDARD: {key}")

                except ClientError as e:
                    print(f"❌ Failed for {key}: {e}")

    except ClientError as e:
        print(f"Error listing objects: {e}")


