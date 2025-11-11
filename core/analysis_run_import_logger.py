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

        self.seq_files = getattr(settings, "SEQUENCING_FILES_SOURCE_DIRECTORY", "")
        self.bucket = getattr(settings, "AWS_STORAGE_BUCKET_NAME", "bastian-lab-169-3-r-us-west-2.sec.ucsf.edu")
        self.region = getattr(settings, "AWS_S3_REGION_NAME", "us-west-2")

        # Clean s3:// prefix if present
        if self.seq_files.startswith("s3://"):
            prefix = f"s3://{self.bucket}/"
            if self.seq_files.startswith(prefix):
                self.seq_files = self.seq_files[len(prefix):]

        # Build proper S3 key
        self.log_key = f"{self.seq_files}/{self.sheet_name}/parse_logs/{self.log_filename}".lstrip("/")

        # Store the S3 URL for this analysis run
        self.log_url = f"s3://{self.bucket}/{self.log_key}"
        _last_log_paths[self.ar_name] = self.log_url

    def _build_header(self):
        """Build formatted header for log file."""
        return f"""
            {'=' * 80}
            Analysis Run Import Log
            {'=' * 80}
            Analysis Run: {self.ar_name}
            Sheet Name: {self.sheet_name}
            Timestamp: {self.timestamp}
            Total Files: {self.total_files}
            Log File: {self.log_filename}
            {'=' * 80}
        """

    def update_total_files(self, total_files):
        """Updates the total files count."""
        self.total_files = total_files
        header = self._build_header()
        self.buffer.write(header + "\n\n")

    def emit(self, record):
        """Write log record to buffer."""
        try:
            msg = self.format(record)
            self.buffer.write(msg + "\n")
        except Exception:
            self.handleError(record)

    def close(self):
        """Upload buffered logs to S3."""
        try:
            s3_client = boto3.client('s3', region_name=self.region)
            log_content = self.buffer.getvalue()

            s3_client.put_object(
                Bucket=self.bucket,
                Key=self.log_key,
                Body=log_content.encode('utf-8'),
                ContentType='text/plain'
            )

        except (NoCredentialsError, ClientError, EndpointConnectionError) as e:
            # Fallback to local file if S3 fails
            downloads_path = os.path.expanduser("~/Downloads")
            local_path = os.path.join(downloads_path, self.log_filename)
            with open(local_path, 'w') as f:
                f.write(self.buffer.getvalue())
        finally:
            self.buffer.close()
            super().close()

    @staticmethod
    def get_log_path(ar_name):
        """Return the most recent log path for a given AnalysisRun name."""
        return _last_log_paths.get(ar_name)

