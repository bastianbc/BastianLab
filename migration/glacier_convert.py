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

s3 = boto3.client("s3", region_name="us-west-2")

BUCKET = "bastian-lab-169-3-r-us-west-2.sec.ucsf.edu"
PREFIX = "BastianRaid-02/HiSeqData/BCB119_NC12685/NC12685/AM2-062/"
PART_SIZE = 500 * 1024 * 1024  # 500 MB per part


def multipart_copy_large_object(key, size):
    print(f"Starting multipart copy for large file: {key} ({size} bytes)")

    # 1. Start multipart upload
    mpu = s3.create_multipart_upload(
        Bucket=BUCKET,
        Key=key,
        StorageClass="STANDARD",
        MetadataDirective="COPY"
    )

    upload_id = mpu["UploadId"]
    parts = []
    part_number = 1

    try:
        # 2. Loop through parts
        for start in range(0, size, PART_SIZE):
            end = min(start + PART_SIZE - 1, size - 1)

            print(f" Copying part {part_number}: bytes {start}-{end}")

            part = s3.upload_part_copy(
                Bucket=BUCKET,
                Key=key,
                CopySource={"Bucket": BUCKET, "Key": key},
                UploadId=upload_id,
                PartNumber=part_number,
                CopySourceRange=f"bytes={start}-{end}"
            )

            parts.append({"ETag": part["CopyPartResult"]["ETag"], "PartNumber": part_number})
            part_number += 1

        # 3. Complete multipart upload
        s3.complete_multipart_upload(
            Bucket=BUCKET,
            Key=key,
            UploadId=upload_id,
            MultipartUpload={"Parts": parts}
        )

        print(f"✓ Completed STANDARD conversion for large object: {key}")

    except Exception as e:
        print(f"❌ Failed during multipart upload: {e}")
        s3.abort_multipart_upload(Bucket=BUCKET, Key=key, UploadId=upload_id)


def convert_prefix():
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=BUCKET, Prefix=PREFIX):
        if "Contents" not in page:
            continue

        for obj in page["Contents"]:
            key = obj["Key"]
            size = obj["Size"]

            if key.endswith("/"):
                continue

            print(f"Processing: {key}")

            # Large file → needs multipart
            if size > 5 * 1024 * 1024 * 1024:
                multipart_copy_large_object(key, size)
                continue

            # Small file → use regular copy
            try:
                s3.copy_object(
                    Bucket=BUCKET,
                    CopySource={"Bucket": BUCKET, "Key": key},
                    Key=key,
                    StorageClass="STANDARD",
                    MetadataDirective="COPY"
                )
                print(f"✓ Converted small file to STANDARD: {key}")
            except ClientError as e:
                print(f"❌ Failed for {key}: {e}")




