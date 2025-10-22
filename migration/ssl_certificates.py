import os
import django

# --- Django boot ---
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test1.settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()

from pathlib import Path
import sys
import hashlib
import boto3
from botocore.exceptions import ClientError, BotoCoreError

# --- AWS / S3 config ---
AWS_REGION  = "us-west-2"
BUCKET_NAME = "bastian-lab-169-3-r-us-west-2.sec.ucsf.edu"
PREFIX      = "ssl certificates/"   # NOTE the space; keep trailing slash
DEST_DIR    = "/etc/ssl/melanomalab"  # change if you want another location
DRY_RUN     = False                  # set True to see what would happen

# --- Optional: only pull typical cert/key files (set to None to download all) ---
ALLOW_EXTENSIONS = {".pem", ".crt", ".cer", ".key", ".p7b", ".p7c", ".der"}

def md5_file(path: Path) -> str:
    """Return an md5 hex digest for a local file (ETag-compatible for single-part uploads)."""
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def should_download(local_path: Path, s3_etag: str) -> bool:
    """
    Decide if we should download.
    - If file missing -> True
    - If ETag (without quotes) matches local MD5 -> skip
    - Else -> True
    """
    if not local_path.exists():
        return True
    # Some S3 ETags are quoted; strip quotes.
    etag = s3_etag.strip('"')
    # For multipart uploads ETag is not a simple MD5; force download in that case.
    if "-" in etag:
        return True
    try:
        return md5_file(local_path) != etag
    except Exception:
        return True

def safe_join(base: Path, relative_key: str) -> Path:
    """
    Join S3 key (relative to PREFIX) into DEST_DIR safely.
    """
    rel = relative_key.lstrip("/").replace("\\", "/")
    return (base / rel).resolve()

def download_prefix(bucket: str, prefix: str, dest_dir: str, allow_ext: set | None = ALLOW_EXTENSIONS) -> None:
    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)

    session = boto3.Session(region_name=AWS_REGION)
    s3 = session.client("s3")
    paginator = s3.get_paginator("list_objects_v2")

    total = 0
    downloaded = 0
    skipped = 0

    try:
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            for obj in page.get("Contents", []):
                key = obj["Key"]
                if key.endswith("/"):
                    # skip "folder" markers
                    continue

                rel_key = key[len(prefix):] if key.startswith(prefix) else key
                target_path = safe_join(Path(dest_dir), rel_key)

                if allow_ext is not None and Path(key).suffix.lower() not in allow_ext:
                    # skip non-cert files if filter enabled
                    continue

                total += 1
                target_path.parent.mkdir(parents=True, exist_ok=True)

                etag = obj.get("ETag", "")
                need = should_download(target_path, etag)

                action = "DOWNLOAD" if need else "SKIP"
                print(f"[{action}] s3://{bucket}/{key} -> {target_path}")

                if DRY_RUN:
                    continue

                if not need:
                    skipped += 1
                    continue

                s3.download_file(bucket, key, str(target_path))
                # Set sane permissions: keys (priv) 600; others 644
                if target_path.suffix.lower() == ".key":
                    target_path.chmod(0o600)
                else:
                    target_path.chmod(0o644)
                downloaded += 1

    except (ClientError, BotoCoreError) as e:
        print(f"ERROR: Failed during S3 sync: {e}", file=sys.stderr)
        sys.exit(2)

    print(f"\nDone. Considered: {total}, Downloaded: {downloaded}, Skipped (up-to-date): {skipped}")
    print(f"Local directory: {dest_dir}")

if __name__ == "__main__":
    # You can toggle DRY_RUN at the top, or via env var if you prefer:
    # DRY_RUN = os.getenv("DRY_RUN", "false").lower() in ("1", "true", "yes")

    # Quick sanity message about the space in the prefix
    if not PREFIX.endswith("/"):
        print("WARNING: PREFIX does not end with '/'; adding it might avoid name collisions.")

    download_prefix(BUCKET_NAME, PREFIX, DEST_DIR, ALLOW_EXTENSIONS)
