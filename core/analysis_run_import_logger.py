import logging
import io
import os
from datetime import datetime
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import s3fs
from botocore.exceptions import NoCredentialsError, ClientError


class S3StorageLogHandler(logging.Handler):
    """Writes import logs to S3 (production) or local Downloads folder (development),
    with a formatted banner header for clarity."""

    def __init__(self, ar_name, total_files=None):
        super().__init__()
        self.ar_name = ar_name
        self.total_files = total_files or "Unknown"
        self.buffer = io.StringIO()
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_filename = f"{self.ar_name}_import_{self.timestamp.replace(':', '').replace(' ', '_')}.log"
        self.log_key = f"logs/{self.log_filename}"

        # ✨ Add beautiful header at the top
        header = self._build_header()
        self.buffer.write(header + "\n\n")

    def _build_header(self):
        line = "=" * 100
        return (
            f"\n{line}\n"
            f"🧬 VARIANT IMPORT LOG\n"
            f"{line}\n"
            f"📁 Analysis Run Name: {self.ar_name}\n"
            f"📦 Total Files: {self.total_files}\n"
            f"⏰ Start Time: {self.timestamp}\n"
            f"🌐 Destination: {getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'Local/Downloads')}\n"
            f"{line}\n"
        )

    def emit(self, record):
        msg = self.format(record)
        self.buffer.write(msg + "\n")

    def close(self):
        content = self.buffer.getvalue()
        self.buffer.close()
        super().close()

        try:
            # ✅ Try S3 upload
            if not getattr(settings, "AWS_STORAGE_BUCKET_NAME", None):
                raise RuntimeError("AWS S3 settings not found")

            default_storage.save(self.log_key, ContentFile(content))
            print(f"✅ Log saved to S3: s3://{default_storage.bucket_name}/{self.log_key}")

        except (NoCredentialsError, ClientError, RuntimeError, Exception) as e:
            # ⚠️ Fallback to local Downloads
            downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
            os.makedirs(downloads_dir, exist_ok=True)
            local_path = os.path.join(downloads_dir, self.log_filename)
            with open(local_path, "w") as f:
                f.write(content)
            print(f"⚠️ Failed to upload log to S3 ({e}); saved locally to: {local_path}")

    def write_test_log(self):
        """Direct test for S3 connectivity using s3fs."""
        try:
            fs = s3fs.S3FileSystem(
                anon=False,
                client_kwargs={
                    "region_name": "us-west-2",
                    "endpoint_url": "https://s3.us-west-2.amazonaws.com",
                },
                config_kwargs={"signature_version": "s3v4"},
            )
            bucket_path = "bastian-lab-169-3-r-us-west-2.sec.ucsf.edu/logs/test_connection.log"
            with fs.open(bucket_path, "w") as f:
                f.write("✅ Connected to S3 successfully via ADFS & s3fs!\n")
            print(f"✅ Test log written to s3://{bucket_path}")
        except Exception as e:
            downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
            os.makedirs(downloads_dir, exist_ok=True)
            test_path = os.path.join(downloads_dir, "test_connection.log")
            with open(test_path, "w") as f:
                f.write(f"⚠️ S3 test failed: {e}\nSaved locally instead.")
            print(f"⚠️ S3 connection test failed, log saved to: {test_path}")
