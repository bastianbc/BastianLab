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




from django.db import transaction

from sequencingfile.models import SMBDirectory  # <-- adjust to your app

AWS_REGION  = "us-west-2"
BUCKET_NAME = "bastian-lab-169-3-r-us-west-2.sec.ucsf.edu"
DRY_RUN     = False

# Map S3 classes to your two levels
STANDARD_CLASSES = {"STANDARD", "STANDARD_IA", "ONEZONE_IA", "INTELLIGENT_TIERING"}
GLACIER_CLASSES  = {"GLACIER", "GLACIER_IR", "DEEP_ARCHIVE"}

def classify(storage_class: str) -> int:
    if not storage_class or storage_class in STANDARD_CLASSES:
        return 0
    if storage_class in GLACIER_CLASSES:
        return 1
    return 0

def strip_volumes_prefix(path: str) -> str:
    """
    Turn '/Volumes/sequencingdata/.../file.ext' into 'sequencingdata/.../file.ext'
    Leaves other paths unchanged.
    """
    prefixes = ["/Volumes/", "/mnt/labshare/"]
    for p in prefixes:
        if path.startswith(p):
            return path[len(p):]
    return path.lstrip("/")

def register_missing_from_db():
    s3 = boto3.client("s3", region_name=AWS_REGION)

    # Only rows not registered yet (per your screenshot)
    rows = SMBDirectory.objects.filter(is_registered=False)[:100]

    total = found = updated = missing = errors = 0
    for row in rows:
        total += 1
        local_path = row.directory or ""
        key = local_path

        # Skip empty or folder markers
        if not key or key.endswith("/"):
            missing += 1
            print(f"⏭️  Skip invalid/dir entry: {local_path}")
            continue

        try:
            print(BUCKET_NAME, key)
            head = s3.head_object(Bucket=BUCKET_NAME, Key=key)
            print(head)
            storage_class = head.get("StorageClass", "STANDARD")
            level = classify(storage_class)
            found += 1

            print(f"🔎 {local_path} → key='{key}' → {storage_class} → level={level} ({'glacier' if level==1 else 'standard'})")

            if DRY_RUN:
                continue

            with transaction.atomic():
                row.storage_level = level
                row.is_registered = True
                # date_registered is set in model.save() when is_registered becomes True
                row.save()
                updated += 1

        except ClientError as e:
            code = e.response.get("Error", {}).get("Code")
            if code in ("404", "NoSuchKey", "NotFound"):
                missing += 1
                print(f"❓ Not found in S3: key='{key}' (from '{local_path}')")
            else:
                errors += 1
                print(f"❌ head_object error for key='{key}': {e}")

    print(f"\nDone. Total {total} | Found {found} | Updated {updated} | Missing {missing} | Errors {errors}")

