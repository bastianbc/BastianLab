import boto3
from botocore.exceptions import ClientError
from boto3.s3.transfer import TransferConfig

AWS_REGION = "us-west-2"
BUCKET_NAME = "bastian-lab-169-3-r-us-west-2.sec.ucsf.edu"  # your bucket
PREFIX = ""          # e.g., "BastianRaid-02/HiSeqData/" or "" for the whole bucket
DRY_RUN = False      # set True first to preview changes

# Multipart copy config (adjust part size / concurrency as needed)
CONFIG = TransferConfig(
    multipart_threshold=8 * 1024 * 1024,    # >8MB uses multipart
    multipart_chunksize=64 * 1024 * 1024,   # 64MB parts
    max_concurrency=10,
    use_threads=True
)

def convert_glacier():
    # If you use a custom endpoint, uncomment endpoint_url:
    # s3 = boto3.resource("s3", region_name=AWS_REGION,
    #                     endpoint_url="https://s3.us-west-2.amazonaws.com")
    s3 = boto3.resource("s3", region_name=AWS_REGION)
    client = s3.meta.client
    bucket = s3.Bucket(BUCKET_NAME)

    total = changed = skipped = errors = 0

    for obj in bucket.objects.filter(Prefix=PREFIX):
        key = obj.key
        total += 1

        # Skip "folder markers"
        if key.endswith("/") and obj.size == 0:
            skipped += 1
            print(f"⏭️  Skip folder marker: {key}")
            continue

        # Check current storage class
        try:
            head = client.head_object(Bucket=BUCKET_NAME, Key=key)
        except ClientError as e:
            errors += 1
            print(f"❌ head_object failed for {key}: {e}")
            continue

        storage_class = head.get("StorageClass", "STANDARD")
        if storage_class == "DEEP_ARCHIVE":
            skipped += 1
            print(f"✅ Already DEEP_ARCHIVE: {key}")
            continue

        copy_source = {"Bucket": BUCKET_NAME, "Key": key}
        extra_args = {
            "StorageClass": "DEEP_ARCHIVE",
            "MetadataDirective": "COPY",   # keep existing metadata
        }

        try:
            if DRY_RUN:
                print(f"🔎 DRY-RUN would change to DEEP_ARCHIVE: {key}")
            else:
                # Multipart-capable self-copy to change storage class
                s3.Object(BUCKET_NAME, key).copy(
                    copy_source,
                    ExtraArgs=extra_args,
                    Config=CONFIG
                )
                changed += 1
                print(f"🔄 Changed to DEEP_ARCHIVE: {key}")
        except ClientError as e:
            errors += 1
            print(f"❌ Error updating {key}: {e}")

    print(f"\nDone. Scanned {total} | Changed {changed} | Skipped {skipped} | Errors {errors}")

