
from boto3.s3.transfer import TransferConfig
import os
import argparse, time
import boto3
from botocore.exceptions import ClientError
from django.db import transaction

from sequencingfile.models import SMBDirectory  # <-- adjust to your app
from qc.models import SampleQC

AWS_REGION = "us-west-2"
BUCKET_NAME = "bastian-lab-169-3-r-us-west-2.sec.ucsf.edu"
DRY_RUN = False   # set True first to preview changes


# Map S3 classes to your two levels
STANDARD_CLASSES = {"STANDARD", "STANDARD_IA", "ONEZONE_IA", "INTELLIGENT_TIERING"}
GLACIER_CLASSES  = {"GLACIER", "GLACIER_IR", "DEEP_ARCHIVE"}


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

import posixpath
from urllib.parse import urlparse
import boto3
from botocore.exceptions import ClientError

KMS_ALIAS   = "alias/managed-s3-key"  # set "" if not using SSE-KMS

ARCHIVE = {"GLACIER", "DEEP_ARCHIVE"}
STANDARDISH = {"STANDARD", "STANDARD_IA", "ONEZONE_IA", "INTELLIGENT_TIERING", "GLACIER_IR"}

def _bucket_key_from_path(path: str):
    """Accepts key prefix, s3:// URL, or https S3 URL; returns (bucket, key)."""
    p = (path or "").strip()
    if not p:
        return (BUCKET_NAME, "")
    if p.startswith("s3://"):
        u = urlparse(p)
        return (u.netloc or BUCKET_NAME, u.path.lstrip("/"))
    if p.startswith(("http://", "https://")):
        u = urlparse(p)
        host, keypath = u.netloc, u.path.lstrip("/")
        if ".s3." in host:                      # virtual-hosted
            bucket = host.split(".s3.")[0]
            return (bucket, keypath)
        parts = keypath.split("/", 1)           # path-style
        return (parts[0], parts[1] if len(parts) == 2 else "")
    # treat as plain key
    return (BUCKET_NAME, p.lstrip("/"))

def _to_key(directory: str, filename: str) -> (str, str):
    bucket, prefix = _bucket_key_from_path(directory)
    key = posixpath.join(prefix.strip("/"), (filename or "").lstrip("/")) if filename else prefix
    return bucket, key

def _copy_to_standard(s3_res, bucket, key):
    src = {"Bucket": bucket, "Key": key}
    extra = {"StorageClass": "STANDARD", "MetadataDirective": "COPY"}
    if KMS_ALIAS:
        extra.update({"ServerSideEncryption": "aws:kms", "SSEKMSKeyId": KMS_ALIAS})
    if DRY_RUN:
        print(f"DRY: copy STANDARD {bucket}/{key}")
        return
    s3_res.Object(bucket, key).copy(src, ExtraArgs=extra)
    print(f"✅ STANDARD: {bucket}/{key}")

def _request_restore(s3_cli, bucket, key, tier="Standard", days=7):
    try:
        if DRY_RUN:
            print(f"DRY: restore {bucket}/{key} (tier={tier})")
            return
        s3_cli.restore_object(Bucket=bucket, Key=key,
                              RestoreRequest={"Days": days, "GlacierJobParameters": {"Tier": tier}})
        print(f"🕒 restore requested: {bucket}/{key}")
    except ClientError as e:
        print(e)

def make_qc_standard():
    s3_res = boto3.resource("s3", region_name=AWS_REGION)
    s3_cli = s3_res.meta.client

    rows = SampleQC.objects.all().select_related("variant_file")  # filter as you wish

    for row in rows:
        # Build the “local” path you were using, then translate to (bucket,key)
        local_path = posixpath.join(row.variant_file.directory or "", row.insert_size_histogram or "")
        bucket, key = _bucket_key_from_path(local_path)

        if not key or key.endswith("/"):
            print(f"⏭️  skip invalid: {local_path}")
            continue

        try:
            h = s3_cli.head_object(Bucket=bucket, Key=key)
        except ClientError as e:
            code = e.response.get("Error", {}).get("Code")
            print(f"❌ head_object {bucket}/{key}: {code}")
            continue

        sc = h.get("StorageClass", "STANDARD")
        restore = h.get("Restore", "")

        if sc == "STANDARD":
            print(f"✅ already STANDARD: {bucket}/{key}")
            continue

        if sc in STANDARDISH:
            _copy_to_standard(s3_res, bucket, key)
            continue

        if sc in ARCHIVE:
            if 'ongoing-request="false"' in str(restore):
                _copy_to_standard(s3_res, bucket, key)
            else:
                _request_restore(s3_cli, bucket, key, tier="Standard", days=7)
            continue

        print(f"ℹ️ unknown class {sc}: {bucket}/{key}")
