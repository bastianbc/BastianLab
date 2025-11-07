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
            # --- 🧩 Detect AWS-managed access log files ---
            if key.startswith("managed-"):
                skipped += 1
                continue

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


BUCKET_NAME = "managed-039612868981-server-access-logs"

s3 = boto3.client("s3")

def delete_all_objects(bucket):
    paginator = s3.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=bucket)

    deleted = 0
    for page in pages:
        if "Contents" in page:
            # Prepare a batch of up to 1000 keys (S3 limit per delete request)
            objects_to_delete = [{"Key": obj["Key"]} for obj in page["Contents"]]
            response = s3.delete_objects(
                Bucket=bucket,
                Delete={"Objects": objects_to_delete, "Quiet": True}
            )
            deleted += len(objects_to_delete)
            print(f"Deleted {deleted} objects so far...")

    print(f"\n✅ Completed — all objects deleted from {bucket}")

if __name__ == "__main__":
    delete_all_objects(BUCKET_NAME)









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






def calculate_size():
    BUCKET_NAME = "bastian-lab-169-3-r-us-west-2.sec.ucsf.edu"
    REGION = "us-west-2"

    s3 = boto3.client("s3", region_name=REGION)
    storage_stats = defaultdict(int)
    standard_folders = defaultdict(int)
    continuation_token = None

    print(f"Scanning bucket: {BUCKET_NAME} in region {REGION} ...")

    while True:
        list_kwargs = {"Bucket": BUCKET_NAME, "MaxKeys": 1000}
        if continuation_token:
            list_kwargs["ContinuationToken"] = continuation_token

        response = s3.list_objects_v2(**list_kwargs)

        if "Contents" not in response:
            break

        for obj in response["Contents"]:
            size = obj["Size"]
            storage_class = obj.get("StorageClass", "STANDARD")

            storage_stats[storage_class] += size

            # If file is STANDARD, track its parent folder
            if storage_class == "STANDARD":
                key = obj["Key"]
                parent = key.split("/")[0] if "/" in key else "(root)"
                standard_folders[parent] += size

        if response.get("IsTruncated"):
            continuation_token = response["NextContinuationToken"]
        else:
            break

    # --- PRINT STORAGE CLASS SUMMARY ---
    print("\n📊 Storage Breakdown by Class:")
    total_bytes = sum(storage_stats.values())
    for storage_class, bytes_used in storage_stats.items():
        gb_used = bytes_used / (1024 ** 3)
        tb_used = bytes_used / (1024 ** 4)
        print(f"  • {storage_class:<15} {gb_used:,.2f} GB  ({tb_used:,.2f} TB)")

    print(f"\nTotal Size: {total_bytes / (1024 ** 4):,.2f} TB ({total_bytes / (1024 ** 3):,.2f} GB)")

    # --- PRINT PARENT FOLDER SIZES (STANDARD ONLY) ---
    print("\n📁 Top-level folders for STANDARD class:")
    sorted_folders = sorted(standard_folders.items(), key=lambda x: x[1], reverse=True)
    for folder, bytes_used in sorted_folders[:15]:  # top 15 folders
        gb_used = bytes_used / (1024 ** 3)
        print(f"  • {folder:<40} {gb_used:,.2f} GB")



