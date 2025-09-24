import os
import django

# --- Django boot ---
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test1.settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()

from pathlib import Path
import boto3
from botocore.exceptions import ClientError
from sequencingfile.models import SMBDirectory

# --- AWS / S3 config ---
AWS_REGION   = "us-west-2"
BUCKET_NAME  = "bastian-lab-169-3-r-us-west-2.sec.ucsf.edu"
S3_TEXT_KEYS = [
    "uploads/captured_lib_pdf_attachments/file_tree_06_21_BastianRaid-02.txt",
    # "uploads/captured_lib_pdf_attachments/file_tree_06_17_sequencingdata.txt",
]
DRY_RUN = False


def _read_s3_lines(s3, bucket: str, key: str):
    """Read a UTF-8 text file from S3 and return non-empty, stripped lines."""
    try:
        obj = s3.get_object(Bucket=bucket, Key=key)
    except ClientError as e:
        raise RuntimeError(f"Failed to read s3://{bucket}/{key}: {e}") from e

    body = obj["Body"].read()
    text = body.decode("utf-8", errors="replace")
    # strip whitespace, drop empties
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return lines


def _normalize(path: str) -> str:
    """Normalize paths a bit: remove './', collapse //, trim spaces."""
    p = path.strip()
    if p.startswith("./"):
        p = p[2:]
    while "//" in p:
        p = p.replace("//", "/")
    return p


def register_smb_from_s3():
    s3 = boto3.client("s3", region_name=AWS_REGION)

    seen = set()
    total, created_count, skipped = 0, 0, 0

    for key in S3_TEXT_KEYS:
        print(f"[S3] Reading: s3://{BUCKET_NAME}/{key}")
        for raw in _read_s3_lines(s3, BUCKET_NAME, key):
            total += 1
            # ignore directory markers & mac cruft
            if raw.endswith("/") or raw.endswith("/.DS_Store"):
                skipped += 1
                continue

            directory = _normalize(raw)
            if directory in seen:
                skipped += 1
                continue
            seen.add(directory)

            if DRY_RUN:
                print(f"DRY_RUN: would register '{directory}'")
                continue

            obj, created = SMBDirectory.objects.get_or_create(directory=directory)
            if created:
                created_count += 1
            else:
                skipped += 1
            print(skipped, created_count, total)
    print(
        f"Done. total={total}, unique_considered={len(seen)}, "
        f"created={created_count}, skipped={skipped}, dry_run={DRY_RUN}"
    )





# import os
# import django
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test1.settings")
# os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
# django.setup()
# import pandas as pd
# from django.conf import settings
# from sequencingfile.models import SMBDirectory
# from pathlib import Path
import pandas as pd
#
#
# bastian-lab-169-3-r-us-west-2.sec.ucsf.edu
# media_files/
# Upload
# file_tree_06_21_BastianRaid-02.txt
# file_tree_06_17_sequencingdata.txt
def register_smb():
    output_file = Path("/Users/cbagci/Documents/test/venv/file_tree_06_21_BastianRaid-02.txt")
    output_file = Path("/Users/cbagci/Documents/test/venv/file_tree_06_17_sequencingdata.txt")

    with open(output_file, "r") as f:
        lines = [line.strip() for line in f if line.strip()]  # remove empty lines

    df = pd.DataFrame(lines, columns=["path"])
    df = df[~df["path"].str.endswith(("/"))]
    df = df[~df["path"].str.endswith(("/.DS_Store"))]
    for path in df["path"]:
        obj, created = SMBDirectory.objects.get_or_create(directory=path.strip())



if __name__ == "__main__":
    print("start")
    register_smb()
    print("end")