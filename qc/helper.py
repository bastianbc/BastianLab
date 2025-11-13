import os
import pandas as pd
import logging
import s3fs
import io
import csv
import sys
from urllib.parse import urlparse
import boto3
from collections import defaultdict
from qc.models import SampleQC
from samplelib.models import SampleLib
from sequencingrun.models import SequencingRun

logger = logging.getLogger(__name__)

BASE_DIR = "/sequencingdata/ProcessedData/"

QC_FILE_EXTENSIONS = {
    "dup_metrics": ".dup_metrics",
    "hs_metrics": ".Hs_Metrics.txt",
    "insert_metrics": ".insert_size_metrics.txt",
    "histogram_pdf": ".Tumor_insert_size_histogram.pdf"
}
EXCEPTION_STATS = defaultdict(int)

EXCEPTION_CODES = {
    # --- Metrics (QC) parsing ---
    "MET000": "SampleLib / SequencingRun not detected",
    "MET001": "Error processing metrics for sample",
    "MET002": "Unrecognized metrics file type",
    "MET003": "Metrics file parsing exception",
    "MET004": "Missing or unreadable metrics file",
    "MET005": "Error saving SampleQC record",
    "MET999": "Unhandled metrics parsing error",
}
def log_and_track_exception(code, message, exception_obj=None, **kwargs):
    """Helper to log error with code and update stats."""
    code_msg = EXCEPTION_CODES.get(code, "UNKNOWN ERROR")
    log_msg = f"[{code}: {code_msg}] {message}"
    # Track stats by function code
    EXCEPTION_STATS[code] += 1
    if exception_obj:
        logger.error(log_msg, exc_info=True, extra=kwargs)
    else:
        logger.error(log_msg, extra=kwargs)


def read_s3_metrics_file(file_path, sep='\t', skiprows=6):
    """
    Reads a metrics file (dup, hs, insert, etc.) from S3 or local disk into a pandas DataFrame.
    Automatically converts HTTPS S3 URLs to s3:// format and handles AWS SSO sessions.
    Skips non-text attachments (PDF/PNG).
    """
    logger.info(f"Reading metrics file: {file_path}")

    # --- Step 0: Early skip for attachments ---
    if file_path.endswith((".pdf", ".png")):
        msg = f"Skipping non-text metrics file: {file_path}"
        log_and_track_exception("MET004", msg)
        return None

    s3_client = boto3.client("s3")
    fs = s3fs.S3FileSystem(anon=False)

    # --- Step 1: Normalize URL to s3:// form ---
    s3_path = file_path
    try:
        if file_path.startswith("https://s3."):
            parsed = urlparse(file_path)
            if parsed.netloc.endswith("amazonaws.com"):
                bucket_and_key = parsed.path.lstrip("/").split("/", 1)
                if len(bucket_and_key) == 2:
                    bucket, key = bucket_and_key
                    s3_path = f"s3://{bucket}/{key}"
            logger.debug(f"Converted HTTPS URL to S3 path: {s3_path}")
        elif file_path.startswith(("http://", "https://")):
            parsed = urlparse(file_path)
            bucket_and_key = parsed.path.lstrip("/").split("/", 1)
            if len(bucket_and_key) == 2:
                bucket, key = bucket_and_key
                s3_path = f"s3://{bucket}/{key}"
            logger.debug(f"Converted generic HTTP URL to S3 path: {s3_path}")
    except Exception as e:
        log_and_track_exception("MET004", f"URL normalization failed for '{file_path}'", e)

    # --- Step 2: Read file content ---
    content = None
    try:
        if s3_path.startswith("s3://"):
            parsed = urlparse(s3_path)
            bucket = parsed.netloc
            key = parsed.path.lstrip("/")
            logger.debug(f"Opening file from S3: bucket={bucket}, key={key}")

            try:
                obj = s3_client.get_object(Bucket=bucket, Key=key)
                content = obj["Body"].read().decode("utf-8", errors="ignore")
            except s3_client.exceptions.NoSuchKey:
                msg = f"Metrics file not found in S3: {s3_path}"
                log_and_track_exception("MET004", msg)
                logger.error(msg)
                return None
        else:
            logger.debug(f"Opening local metrics file: {file_path}")
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
    except Exception as e:
        log_and_track_exception("MET004", f"Failed to read file '{file_path or s3_path}'", e)
        raise

    # --- Step 3: Parse TSV content into DataFrame ---
    try:
        lines = [ln for ln in content.strip().split("\n") if ln.strip()]
        if not lines:
            raise ValueError(f"Empty metrics file: {file_path}")

        # Skip Picard headers (if any)
        csv.field_size_limit(min(sys.maxsize, 2147483647))
        reader = csv.reader(io.StringIO(content), delimiter=sep)

        # If skiprows specified (Picard has ~6 metadata lines)
        for _ in range(skiprows):
            next(reader, None)

        rows = list(reader)
        if not rows or len(rows) < 2:
            raise ValueError(f"No valid data rows found in metrics file: {file_path}")

        df = pd.DataFrame(rows[1:], columns=rows[0])
        logger.info(f"✅ Parsed metrics file successfully — {len(df)} rows, {len(df.columns)} columns.")
        return df

    except Exception as e:
        log_and_track_exception("MET004", f"Failed to parse metrics file '{file_path}'", e)
        raise


def parse_dup_metrics(file_path):
    """
    Parse duplicate metrics file and extract required values.
    The table starts at row 7.
    """
    try:
        # Read the file with pandas
        df = read_s3_metrics_file(file_path)

        # Check if data is present
        if df.empty or len(df) < 2:
            logger.warning(f"Empty or incomplete data in {file_path}")
            return {}

        # Extract row from index 1 (after skipping 6 rows, this is row 7-8)
        row = df.iloc[0]

        # Extract metrics
        metrics = {
            'unpaired_reads_examined': row.get('UNPAIRED_READS_EXAMINED'),
            'read_pairs_examined': row.get('READ_PAIRS_EXAMINED'),
            'secondary_or_supplementary_rds': row.get('SECONDARY_OR_SUPPLEMENTARY_RDS'),
            'unmapped_reads': row.get('UNMAPPED_READS'),
            'unpaired_read_duplicates': row.get('UNPAIRED_READ_DUPLICATES'),
            'read_pair_duplicates': row.get('READ_PAIR_DUPLICATES'),
            'read_pair_optical_duplicates': row.get('READ_PAIR_OPTICAL_DUPLICATES'),
            'percent_duplication': row.get('PERCENT_DUPLICATION'),
            'estimated_library_size': row.get('ESTIMATED_LIBRARY_SIZE')
        }

        # Log any missing metrics
        missing_metrics = [k for k, v in metrics.items() if v is None]
        if missing_metrics:
            logger.warning(f"Missing metrics in {file_path}: {', '.join(missing_metrics)}")

        return metrics

    except Exception as e:
        logger.error(f"Error parsing duplicate metrics file {file_path}: {str(e)}")
        return {}

def parse_hs_metrics(file_path):
    """
    Parse Hs metrics file and extract required values.
    The table starts at row 7.
    """
    try:
        # Read the file with pandas
        df = read_s3_metrics_file(file_path)

        # Check if data is present
        if df.empty or len(df) < 2:
            logger.warning(f"Empty or incomplete data in {file_path}")
            return {}

        # Extract row from index 1 (after skipping 6 rows, this is row 7-8)
        row = df.iloc[0]

        # Extract metrics
        metrics = {
            'pct_off_bait': row.get('PCT_OFF_BAIT'),
            'mean_bait_coverage': row.get('MEAN_BAIT_COVERAGE'),
            'mean_target_coverage': row.get('MEAN_TARGET_COVERAGE'),
            'median_target_coverage': row.get('MEDIAN_TARGET_COVERAGE'),
            'pct_target_bases_1x': row.get('PCT_TARGET_BASES_1X'),
            'pct_target_bases_2x': row.get('PCT_TARGET_BASES_2X'),
            'pct_target_bases_10x': row.get('PCT_TARGET_BASES_10X'),
            'pct_target_bases_20x': row.get('PCT_TARGET_BASES_20X'),
            'pct_target_bases_30x': row.get('PCT_TARGET_BASES_30X'),
            'pct_target_bases_40x': row.get('PCT_TARGET_BASES_40X'),
            'pct_target_bases_50x': row.get('PCT_TARGET_BASES_50X'),
            'pct_target_bases_100x': row.get('PCT_TARGET_BASES_100X'),
            'at_dropout': row.get('AT_DROPOUT'),
            'gc_dropout': row.get('GC_DROPOUT')
        }

        # Log any missing metrics
        missing_metrics = [k for k, v in metrics.items() if v is None]
        if missing_metrics:
            logger.warning(f"Missing metrics in {file_path}: {', '.join(missing_metrics)}")

        return metrics

    except Exception as e:
        logger.error(f"Error parsing Hs metrics file {file_path}: {str(e)}")
        return {}

def parse_insert_size_metrics(file_path):
    """
    Parse insert size metrics file and extract required values.
    The table starts at row 7.
    """
    try:
        # Read the file with pandas
        df = read_s3_metrics_file(file_path)
        # Check if data is present
        if df.empty or len(df) < 2:
            logger.warning(f"Empty or incomplete data in {file_path}")
            return {}

        # Extract row from index 1 (after skipping 6 rows, this is row 7-8)
        row = df.iloc[0]

        # Extract metrics
        metrics = {
            'median_insert_size': row.get('MEDIAN_INSERT_SIZE'),
            'mode_insert_size': row.get('MODE_INSERT_SIZE'),
            'mean_insert_size': row.get('MEAN_INSERT_SIZE')
        }

        # Log any missing metrics
        missing_metrics = [k for k, v in metrics.items() if v is None]
        if missing_metrics:
            logger.warning(f"Missing metrics in {file_path}: {', '.join(missing_metrics)}")

        return metrics

    except Exception as e:
        logger.error(f"Error parsing insert size metrics file {file_path}: {str(e)}")
        return {}

def group_qc_files_by_sample(qc_files):
    """
    Group QC files by sample library ID.

    Args:
        qc_files: List of dictionaries with QC file info

    Returns:
        Dictionary mapping sample library IDs to their QC files
    """
    sample_libraries = defaultdict(lambda: {'files': {}})

    for file_info in qc_files:
        sample_lib_name = file_info['sample_lib_name']
        sample_libraries[sample_lib_name]['files'][file_info['file_type']] = file_info['file_path']
        sample_libraries[sample_lib_name]['sequencing_run_name'] = file_info['sequencing_run_name']

    return sample_libraries

def get_sample_lib(file_path):
    """
    Get the sample library from the file path.
    """
    file_name = file_path.split("/")[-1]
    sample_lib_name = file_name.split('.')[1]
    try:
        sample_lib = SampleLib.objects.get(name=sample_lib_name)
        return sample_lib
    except SampleLib.DoesNotExist:
        logger.error(f"SampleLib {sample_lib_name} not found")
        return None

def get_sequencing_run(file_path):
    """
    Get the sequencing run from the file path.
    """
    file_name = file_path.split("/")[-1]
    sequencing_run_name = file_name.split('.')[0]
    try:
        sequencing_run = SequencingRun.objects.get(name=sequencing_run_name)
        return sequencing_run
    except SequencingRun.DoesNotExist:
        logger.error(f"SequencingRun {sequencing_run_name} not found")
        return None


def parse_metrics_files(analysis_run, file_path):
    """
    Incrementally process a single metrics file related to an AnalysisRun.
    Detects the file type from its name and calls the corresponding parser.
    Updates SampleQC record without overwriting existing metrics.
    """

    logger.info(f"📊 Processing single metric file for: {analysis_run.name}")
    file_name = os.path.basename(file_path)
    logger.debug(f"Detected metrics file: {file_name}")

    # --- Identify sample and sequencing context ---
    sample_lib = get_sample_lib(file_path)
    sequencing_run = get_sequencing_run(file_path)
    if not (sample_lib and sequencing_run):
        msg = f"⚠️ Could not determine sample_lib or sequencing_run from {file_name}"
        log_and_track_exception("MET000", msg)
        logger.warning(msg)
        return False, msg, {}

    sample_qc, _ = SampleQC.objects.get_or_create(
        sample_lib=sample_lib,
        sequencing_run=sequencing_run,
        analysis_run=analysis_run,
    )

    stats = {
        "file_name": file_name,
        "parsed": False,
        "errors": [],
    }

    try:
        # --- Decide which parser to run ---
        lower_name = file_name.lower()

        if lower_name.endswith(".dup_metrics"):
            metrics = parse_dup_metrics(file_path)
            sample_qc.dup_metrics_path = file_path
            stats["parsed"] = True
            logger.info(f"🧩 Parsed duplication metrics for {sample_lib.name}")

        elif "hs_metrics" in lower_name or lower_name.endswith("_hs_metrics.txt"):
            metrics = parse_hs_metrics(file_path)
            sample_qc.hs_metrics_path = file_path
            stats["parsed"] = True
            logger.info(f"🧬 Parsed hybrid-selection metrics for {sample_lib.name}")

        elif lower_name.endswith(".insert_size_metrics.txt"):
            metrics = parse_insert_size_metrics(file_path)
            sample_qc.insert_metrics_path = file_path
            stats["parsed"] = True
            logger.info(f"📏 Parsed insert-size metrics for {sample_lib.name}")

        elif lower_name.endswith("_insert_size_histogram.pdf"):
            metrics = None
            sample_qc.insert_size_histogram = file_path
            sample_qc.save()
            stats["parsed"] = True
            logger.info(f"🖼️ Attached insert-size histogram PDF for {sample_lib.name}")

        else:
            msg = f"Unrecognized metrics file type: {file_name}"
            logger.warning(msg)
            log_and_track_exception("MET002", msg)
            return False, msg, stats

        # --- Save metrics incrementally without overwriting previous fields ---
        if metrics:
            for key, val in metrics.items():
                if hasattr(sample_qc, key):
                    setattr(sample_qc, key, val)
            sample_qc.save()

        msg = f"✅ Successfully processed metrics file: {file_name}"
        logger.info(msg)
        return True, msg, stats

    except Exception as e:
        error_msg = f"❌ Error processing metrics file {file_name}: {e}"
        log_and_track_exception("MET003", error_msg, e)
        stats["errors"].append(str(e))
        logger.error(error_msg)
        return False, error_msg, stats
