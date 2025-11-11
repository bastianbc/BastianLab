import logging
import io
import os
import boto3
from datetime import datetime
from django.conf import settings
from botocore.exceptions import NoCredentialsError, ClientError, EndpointConnectionError

_last_log_paths = {}

class S3StorageLogHandler(logging.Handler):
    """Writes import logs to S3 (via boto3) or local Downloads folder as fallback.
    Adds a formatted header for clarity and context."""

    def __init__(self, ar_name, sheet_name, total_files=None):
        super().__init__()
        self.ar_name = ar_name
        self.sheet_name = sheet_name
        self.total_files = total_files or "Unknown"
        self.buffer = io.StringIO()
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_filename = f"{self.ar_name}_import_{self.timestamp.replace(':', '').replace(' ', '_')}.log"

        # Get sequencing directory path from settings and clean any s3:// prefix
        self.seq_files = getattr(settings, "SEQUENCING_FILES_SOURCE_DIRECTORY", "")
        self.bucket = getattr(settings, "AWS_STORAGE_BUCKET_NAME", "bastian-lab-169-3-r-us-west-2.sec.ucsf.edu")
        self.region = getattr(settings, "AWS_S3_REGION_NAME", "us-west-2")

        # 🔧 Clean s3://bucket_name/ prefix if present
        if self.seq_files.startswith("s3://"):
            prefix = f"s3://{self.bucket}/"
            if self.seq_files.startswith(prefix):
                self.seq_files = self.seq_files[len(prefix):]  # remove the full s3://bucket_name/ part

        # ✅ Build proper S3 key (no double s3:// prefix)
        self.log_key = f"{self.seq_files}/{self.sheet_name}/parse_logs/{self.log_filename}".lstrip("/")

        # ✨ Add header immediately
        header = self._build_header()
        self.buffer.write(header + "\n\n")

    @staticmethod
    def get_log_path(ar_name):
        """Return the most recent log path for a given AnalysisRun name."""
        return _last_log_paths.get(ar_name)

    def _build_header(self):
        line = "=" * 100
        return (
            f"\n{line}\n"
            f"🧬 VARIANT IMPORT LOG\n"
            f"{line}\n"
            f"📁 Analysis Run Name: {self.ar_name}\n"
            f"📄 Sheet Name: {self.sheet_name}\n"
            f"📦 Total Files: {self.total_files}\n"
            f"⏰ Start Time: {self.timestamp}\n"
            f"🌐 Destination: {self.bucket}/{self.log_key}\n"
            f"{line}\n"
        )

    def emit(self, record):
        msg = self.format(record)
        self.buffer.write(msg + "\n")

    def close(self):
        """Flush buffer to S3 or fallback to Downloads."""
        try:
            content = self.buffer.getvalue()
        finally:
            self.buffer.close()
            super().close()

        try:
            # ✅ Create S3 client
            s3_client = boto3.client(
                "s3",
                region_name=self.region,
                config=boto3.session.Config(signature_version="s3v4"),
            )

            # ✅ Upload the log file
            s3_client.put_object(
                Bucket=self.bucket,
                Key=self.log_key,
                Body=content.encode("utf-8"),
                ContentType="text/plain",
            )
            _last_log_paths[self.ar_name] = f"s3://{self.bucket}/{self.log_key}"

            print(f"✅ Log uploaded successfully to s3://{self.bucket}/{self.log_key}")

        except (NoCredentialsError, ClientError, EndpointConnectionError, Exception) as e:
            downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
            os.makedirs(downloads_dir, exist_ok=True)
            local_path = os.path.join(downloads_dir, self.log_filename)

            try:
                with open(local_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"⚠️ Failed to upload log to S3 ({e}); saved locally to: {local_path}")
            except Exception as inner_e:
                print(f"❌ Critical error saving log locally: {inner_e}")

    def write_test_log(self):
        """Direct S3 test to verify boto3 access works."""
        try:
            s3_client = boto3.client(
                "s3",
                region_name=self.region,
                config=boto3.session.Config(signature_version="s3v4"),
            )
            test_key = "logs/test_connection.log"
            s3_client.put_object(
                Bucket=self.bucket,
                Key=test_key,
                Body="✅ Connected to S3 successfully via boto3!\n",
                ContentType="text/plain",
            )
            print(f"✅ Test log written to s3://{self.bucket}/{test_key}")
        except Exception as e:
            downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
            os.makedirs(downloads_dir, exist_ok=True)
            test_path = os.path.join(downloads_dir, "test_connection.log")
            with open(test_path, "w") as f:
                f.write(f"⚠️ S3 connection test failed: {e}\nSaved locally instead.")
            print(f"⚠️ S3 connection test failed, saved locally to: {test_path}")
