from sequencingfile.models import SMBDirectory   # adjust import
import boto3
from botocore.exceptions import ClientError
from boto3.s3.transfer import TransferConfig

AWS_REGION = "us-west-2"
BUCKET_NAME = "bastian-lab-169-3-r-us-west-2.sec.ucsf.edu"
DRY_RUN = False   # set True first to preview changes

CONFIG = TransferConfig(
    multipart_threshold=8 * 1024 * 1024,
    multipart_chunksize=64 * 1024 * 1024,
    max_concurrency=10,
    use_threads=True
)

def convert_glacier_and_mark_level():
    s3 = boto3.resource("s3", region_name=AWS_REGION)
    client = s3.meta.client

    # your filter stays the same
    rows = SMBDirectory.objects.filter(is_registered=True, storage_level=0)

    total = changed = skipped = errors = 0

    for row in rows:
        key = row.directory
        total += 1

        # If you have a size field and want to skip folder markers
        if key.endswith("/") and getattr(row, "size", 0) == 0:
            skipped += 1
            print(f"⏭️  Skip folder marker: {key}")
            continue

        # Read current storage class
        try:
            head = client.head_object(Bucket=BUCKET_NAME, Key=key)
        except ClientError as e:
            errors += 1
            print(f"❌ head_object failed for {key}: {e}")
            continue

        storage_class = head.get("StorageClass", "STANDARD")

        # If already DEEP_ARCHIVE, just sync the DB to level=1 (if desired)
        if storage_class == "DEEP_ARCHIVE":
            if row.storage_level != 1 and not DRY_RUN:
                row.storage_level = 1
                row.save(update_fields=["storage_level"])
                print(f"✅ Already DEEP_ARCHIVE, marked storage_level=1: {key}")
            else:
                print(f"✅ Already DEEP_ARCHIVE: {key}")
            skipped += 1
            continue

        # Prepare in-place copy to change storage class
        copy_source = {"Bucket": BUCKET_NAME, "Key": key}
        extra_args = {
            "StorageClass": "DEEP_ARCHIVE",
            "MetadataDirective": "COPY",
        }

        try:
            if DRY_RUN:
                print(f"🔎 DRY-RUN would change to DEEP_ARCHIVE: {key}")
            else:
                s3.Object(BUCKET_NAME, key).copy(
                    copy_source,
                    ExtraArgs=extra_args,
                    Config=CONFIG
                )
                changed += 1
                print(f"🔄 Changed to DEEP_ARCHIVE: {key}")

                # ✅ persist the new level in DB
                row.storage_level = 1
                row.save(update_fields=["storage_level"])
                print(f"💾 Updated DB storage_level=1 for: {key}")

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
    rows = SMBDirectory.objects.filter(is_registered=False)

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
            head = s3.head_object(Bucket=BUCKET_NAME, Key=key)
            storage_class = head.get("StorageClass", "STANDARD")
            level = classify(storage_class)
            found += 1


            if DRY_RUN:
                continue

            with transaction.atomic():
                row.storage_level = level
                row.is_registered = True
                # date_registered is set in model.save() when is_registered becomes True
                row.save()
                updated += 1
            print(found)
        except ClientError as e:
            code = e.response.get("Error", {}).get("Code")
            if code in ("404", "NoSuchKey", "NotFound"):
                missing += 1
                print(f"❓ Not found in S3: key='{key}' (from '{local_path}')")
            else:
                errors += 1
                print(f"❌ head_object error for key='{key}': {e}")

    print(f"\nDone. Total {total} | Found {found} | Updated {updated} | Missing {missing} | Errors {errors}")

def sync_smbdirs_to_s3():
    s3 = boto3.client("s3", region_name=AWS_REGION)

    for smbdir in SMBDirectory.objects.filter():
        try:
            prefix = smbdir.directory.strip("/")
            resp = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix, MaxKeys=1)

            if "Contents" in resp:  # found at least one object
                print(f"{smbdir.directory[-3:]}")
            else:
                smbdir.is_registered = False
                smbdir.save(update_fields=["is_registered"])
                print(f"[MISSING] {smbdir.directory[-3:]} not in S3 - prefix: {prefix[-3:]}")
        except Exception as e:
            print(e)