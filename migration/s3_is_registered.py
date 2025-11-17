# yourapp/management/commands/sync_smb_with_s3.py
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import timedelta

import boto3
from botocore.exceptions import ClientError
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from sequencingfile.models import SMBDirectory  # adjust if your app path differs

AWS_REGION  = "us-west-2"
BUCKET_NAME = "bastian-lab-169-3-r-us-west-2.sec.ucsf.edu"

# Tune these based on instance size and network
MAX_WORKERS   = 16
BATCH_SIZE    = 500      # DB rows per bulk update
QUERY_FILTERS = dict()   # e.g. {"is_registered": False} to target only new rows

# Map S3 StorageClass to your storage_level
STORAGE_LEVEL_MAP = {
    "DEEP_ARCHIVE": 1,
    "GLACIER": 1,
    "GLACIER_IR": 1,
    # everything else → 0
}

def normalize_key(path: str) -> str:
    if not path:
        return path
    # strip '/Volumes/' prefix if present
    if path.startswith("/Volumes/"):
        path = path[len("/Volumes/"):]
    # strip any remaining leading slash
    while path.startswith("/"):
        path = path[1:]
    return path

def s3_object_exists(client, bucket: str, key: str):
    """
    Returns (exists: bool, storage_class: str|None)
    - If 'key' is a file, we read StorageClass from head_object.
    - If 'key' is a 'folder' marker (no object), we probe with list_objects_v2.
    """
    # 1) Try a direct head_object (file)
    try:
        head = client.head_object(Bucket=bucket, Key=key)
        # Some objects may not include StorageClass (STANDARD by default)
        storage_class = head.get("StorageClass", "STANDARD")
        return True, storage_class
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code")
        if code not in ("404", "NoSuchKey", "NotFound"):
            # Other errors (permissions, throttling, etc.) → re-raise
            raise

    # 2) If head fails, try as a prefix (“folder”)
    # Ensure suffix slash for prefix-esque keys
    prefix = key if key.endswith("/") else key + "/"
    resp = client.list_objects_v2(Bucket=bucket, Prefix=prefix, MaxKeys=1)
    has_contents = bool(resp.get("KeyCount", 0))
    if has_contents:
        # Storage class per-object varies; treat as STANDARD for the directory row
        return True, None
    return False, None

def to_storage_level(storage_class: str | None) -> int:
    if storage_class is None:
        # Unknown → assume standard (you can choose to leave as-is instead)
        return 0
    return STORAGE_LEVEL_MAP.get(storage_class, 0)

class Command(BaseCommand):
    help = "Search S3 for keys from smb_directory and update is_registered/date_registered/storage_level."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Do not write to the database; only report.",
        )
        parser.add_argument(
            "--only-unregistered",
            action="store_true",
            help="Only process rows where is_registered=False (faster).",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Process at most N rows (useful for testing).",
        )
        parser.add_argument(
            "--workers",
            type=int,
            default=MAX_WORKERS,
            help=f"Thread pool size (default {MAX_WORKERS}).",
        )

    def handle(self, *args, **opts):
        dry_run   = opts["dry_run"]
        only_unreg = opts["only_unregistered"]
        max_workers = opts["workers"]
        limit       = opts["limit"]

        qs = SMBDirectory.objects.all().only("id", "directory", "is_registered", "storage_level")
        if only_unreg:
            qs = qs.filter(is_registered=False)

        if QUERY_FILTERS:
            qs = qs.filter(**QUERY_FILTERS)

        if limit:
            qs = qs.order_by("id")[:limit]

        total = qs.count()
        if total == 0:
            self.stdout.write(self.style.WARNING("No rows to process."))
            return

        self.stdout.write(self.style.NOTICE(f"Scanning {total} rows against s3://{BUCKET_NAME} (region {AWS_REGION})"))
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN: no database changes will be made."))

        s3 = boto3.session.Session(region_name=AWS_REGION)
        client = s3.client("s3")  # credentials via env/instance profile

        # Work queue
        futures = []
        results = []  # tuples: (row_id, found_bool, new_is_registered, new_storage_level, normalized_key, storage_class)

        def worker(row):
            key_raw = row.directory or ""
            key = normalize_key(key_raw)
            try:
                exists, storage_class = s3_object_exists(client, BUCKET_NAME, key)
                if exists:
                    level = to_storage_level(storage_class)
                    return (row.id, True, True, level, key, storage_class)
                else:
                    return (row.id, False, False, row.storage_level if row.storage_level is not None else 0, key, None)
            except Exception as e:
                # Bubble up; re-raise so we can see errors
                raise

        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            for row in qs.iterator(chunk_size=2000):
                futures.append(pool.submit(worker, row))

            done = 0
            for fut in as_completed(futures):
                res = fut.result()
                results.append(res)
                done += 1
                if done % 500 == 0:
                    self.stdout.write(f"Processed {done}/{total}…")

        # Prepare DB updates
        to_update = []
        now = timezone.now()
        found_cnt = 0
        missing_cnt = 0

        # Fetch a mapping of id->row to avoid extra queries on bulk update
        rows_by_id = {r.id: r for r in SMBDirectory.objects.filter(id__in=[r[0] for r in results]).only("id", "is_registered", "date_registered", "storage_level")}

        for (row_id, found, new_is_registered, new_level, key, storage_class) in results:
            row = rows_by_id[row_id]
            if found:
                found_cnt += 1
                # Decide whether to update fields
                need_update = False
                if row.is_registered is not True:
                    row.is_registered = True
                    need_update = True
                # storage_level: only set if different or null
                if (row.storage_level is None) or (row.storage_level != new_level):
                    row.storage_level = new_level
                    need_update = True
                # date_registered: set when we first confirm presence
                if (row.date_registered is None):
                    row.date_registered = now
                    need_update = True

                if need_update:
                    to_update.append(row)
            else:
                missing_cnt += 1
                # Optionally, you could set is_registered=False; we leave as-is to avoid flip-flopping

        if dry_run:
            self.stdout.write(self.style.WARNING(
                f"DRY RUN SUMMARY — Found: {found_cnt}, Missing: {missing_cnt}, Would update: {len(to_update)}"
            ))
            return

        # Bulk update in batches
        updated = 0
        fields = ["is_registered", "storage_level", "date_registered"]
        with transaction.atomic():
            for i in range(0, len(to_update), BATCH_SIZE):
                chunk = to_update[i:i+BATCH_SIZE]
                SMBDirectory.objects.bulk_update(chunk, fields)
                updated += len(chunk)

        self.stdout.write(self.style.SUCCESS(
            f"Done. Scanned {total} | Found {found_cnt} | Missing {missing_cnt} | Updated {updated}"
        ))
#!/usr/bin/env python3
import subprocess
import logging
from datetime import datetime

SOURCE = "/mnt/smb_volume/ProcessedData/hg38_ProcessedData/Analysis.tumor-normal/Broad/14-July-25/BroadWES1-3/snv/"
BUCKET = "bastian-lab-169-3-r-us-west-2.sec.ucsf.edu"
PREFIX = "sequencingdata/ProcessedData/AR9_dna-v1_hg38/Analysis.tumor-normal/Broad/14-July-25/BroadWES1-3/snv/"
DEST = f"s3://{BUCKET}/{PREFIX}"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(f"s3_sync_{datetime.now():%Y%m%d_%H%M%S}.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)


def run_sync():
    log.info(f"Starting AWS sync")
    log.info(f"Source: {SOURCE}")
    log.info(f"Destination: {DEST}")

    cmd = [
        "aws", "s3", "sync",
        SOURCE, DEST,
        "--only-show-errors",
        "--no-progress",
        "--size-only",          # Skip files if size matches (fast)
        "--exact-timestamps",   # Preserve mod-times
    ]

    try:
        subprocess.check_call(cmd)
        log.info("✓ Sync completed successfully")
    except subprocess.CalledProcessError as e:
        log.error(f"✗ Sync failed: {e}")
