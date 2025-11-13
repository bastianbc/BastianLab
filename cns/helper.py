import os
import csv
import sys
import base64
from PIL import Image
from io import BytesIO
import s3fs
import logging
from collections import defaultdict
from django.conf import settings
from cns.models import Cns
from samplelib.models import SampleLib
from sequencingrun.models import SequencingRun
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import pylab
from urllib.parse import urlparse
from django.db import transaction

logger = logging.getLogger("file")


BASE_PATH = settings.VARIANT_FILES_SOURCE_DIRECTORY

# Global dictionary to hold exception statistics
EXCEPTION_STATS = defaultdict(int)

# --- Exception Codes (for this module) ---
EXCEPTION_CODES = {
    # CNS parsing / IO
    "CNS001": "Folder/Path Error in handle_variant_file",
    "CNS002": "AnalysisRun DoesNotExist",
    "CNS003": "SequencingRun DoesNotExist",
    "CNS004": "SampleLib DoesNotExist",
    "CNS005": "Path/Directory not found (find_folders)",
    "CNS006": "CNS object creation failed (parse_cns_file)",
    "CNS007": "CNS object creation failed (parse_cns_file_with_handler)",
    "CNS008": "Data conversion error (get_float_value)",
    "CNS009": "Error reading CNS file with pandas/S3",
    "CNS010": "Graph generation error",
    "CNS011": "General parsing error (parse_cns_file)",
    "CNS012": "General parsing error (parse_cns_file_with_handler)",
    "CNS013": "File name parsing error (e.g. split)",
    "CNA001": "CNV attachment assignment error",
    "CNA002": "CNV attachment lookup/mismatch",
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


def generate_graph(ar_name,file_path):
 # CSV verilerini okuma
    df = pd.read_csv(file_path)

    # Örneğin, sadece 'chr11' kromozomuna ait verileri filtreleyelim
    df_subset = df[df['chromosome'] == 'chr11']

    # Belirli örnekleri seçelim
    sample_subset = df_subset['start'].unique()[:5]  # İlk 5 örnek
    df_subset = df_subset[df_subset['start'].isin(sample_subset)]

    # Plot the limited subset
    plt.figure(figsize=(10, 6))

    for sample in sample_subset:
        sample_data = df_subset[df_subset['start'] == sample]
        plt.plot(sample_data['start'], sample_data['log2'], label=sample)

    plt.xlabel('Genomic Position')
    plt.ylabel('Log2 Ratio')
    plt.title('Chromosome 11 Segments for Identified Samples')
    plt.legend()

    buffer = BytesIO()
    canvas = pylab.get_current_fig_manager().canvas
    canvas.draw()
    pilImage = Image.frombytes("RGB", canvas.get_width_height(), canvas.tostring_rgb())
    pilImage.save(buffer, "PNG")

    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def get_sequencing_run(file_path):
    try:
        file_name = file_path.split("/")[-1]
        sequencing_run_name = file_name.split(".")[0]
        return SequencingRun.objects.get(name=sequencing_run_name)
    except SequencingRun.DoesNotExist as e:
        log_and_track_exception("CNS003", f"SequencingRun not found: {file_path}", e)
        return None
    except Exception as e:
        log_and_track_exception("CNS003", f"Unexpected error getting SequencingRun from '{file_path}'", e)
        return None


def get_sample_lib(file_path):
    try:
        file_name = file_path.split("/")[-1]
        sample_lib_name = file_name.split(".")[1]
        return SampleLib.objects.get(name=sample_lib_name)
    except SampleLib.DoesNotExist as e:
        log_and_track_exception("CNS004", f"SampleLib not found: {file_path}", e)
        return None
    except Exception as e:
        log_and_track_exception("CNS004", f"Unexpected error getting SampleLib from '{file_path}'", e)
        return None


def read_cns_file(file_path):
    """
    Reads a CNS (Copy Number Segment) file from S3 or local disk into a pandas DataFrame.
    Automatically converts HTTPS S3 URLs to s3:// format.
    Skips non-text (PDF/PNG) attachments.
    """
    logger.info(f"Reading CNS file: {file_path}")

    if file_path.endswith((".pdf", ".png")):
        msg = f"Skipping attachment (not a CNS text file): {file_path}"
        log_and_track_exception("CNS009", msg)
        return None

    fs = s3fs.S3FileSystem(anon=False)

    # Normalize to s3:// if needed
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
        log_and_track_exception("CNS009", f"URL normalization failed for '{file_path}'", e)

    # Read content
    try:
        if s3_path.startswith("s3://"):
            logger.debug(f"Opening file from S3 path: {s3_path}")
            with fs.open(s3_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        else:
            logger.debug(f"Opening local file: {file_path}")
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
    except Exception as e:
        log_and_track_exception("CNS009", f"Failed to read file '{file_path or s3_path}'", e)
        raise

    # Parse TSV content
    try:
        lines = [ln for ln in content.strip().split("\n") if ln.strip()]
        if not lines:
            raise ValueError(f"Empty CNS file: {file_path}")

        headers = lines[0].split("\t")
        header_count = len(headers)
        csv.field_size_limit(min(sys.maxsize, 2147483647))

        data = []
        reader = csv.reader(content.splitlines(), delimiter="\t")
        for row in reader:
            if len(row) < header_count:
                row += [""] * (header_count - len(row))
            elif len(row) > header_count:
                row = row[:header_count]
            data.append(row)

        if len(data) < 2:
            raise ValueError(f"No valid data rows found in CNS file: {file_path}")

        df = pd.DataFrame(data[1:], columns=data[0])
        logger.info(f"✅ Parsed CNS file successfully — {len(df)} rows, {len(df.columns)} columns.")
        return df
    except Exception as e:
        log_and_track_exception("CNS009", f"Failed to parse CNS file '{file_path}'", e)
        raise


def get_float_value(value, default=0.0):
    try:
        return float(value)
    except (ValueError, TypeError) as e:
        log_and_track_exception("CNS008", f"Float conversion failed for {value!r}; using default={default}", e)
        return default


def get_string_value(value, default=""):
    try:
        return str(value) if value is not None else default
    except Exception as e:
        log_and_track_exception("CNS013", f"String conversion failed for {value!r}; using default", e)
        return default


def get_or_none(model_class, **kwargs):
    try:
        return model_class.objects.get(**kwargs)
    except Exception as e:
        log_and_track_exception("CNS011", f"get_or_none failed for {model_class.__name__} with {kwargs}", e)
        return None


@transaction.atomic
def parse_cns_file_with_handler(file_path, analysis_run, variant_file):
    """
    Parse and register CNS files (.cns, .call.cns, .bintest.cns).
    Creates or updates Cns objects based on genomic coordinates.
    Wrapped in a database transaction for atomic integrity.

    Returns:
        (success: bool, message: str, stats: dict)
    """
    stats = {
        "total_rows": 0,
        "successful": 0,
        "failed": 0,
        "created": 0,
        "updated": 0,
        "errors": [],
    }

    try:
        logger.info(f"🧬 Starting variant file parser for {variant_file.name}")

        sequencing_run = get_sequencing_run(file_path)
        sample_lib = get_sample_lib(file_path)

        df = read_cns_file(file_path)
        if df is None:
            msg = f"No content parsed for: {file_path}"
            log_and_track_exception("CNS009", msg)
            stats["errors"].append(msg)
            return False, msg, stats

        df.columns = [c.strip().lower() for c in df.columns]
        stats["total_rows"] = len(df)
        optional_fields = ["ci_hi", "ci_lo", "cn", "p_bintest", "p_ttest"]

        created_objects_count = 0
        updated_objects_count = 0

        # --- Begin atomic transaction ---
        with transaction.atomic():
            for i, row in df.iterrows():
                try:
                    chromosome = row.get("chromosome")
                    start = int(row.get("start", 0))
                    end = int(row.get("end", 0))
                    gene = get_string_value(row.get("gene", ""))
                    log2 = get_float_value(row.get("log2", 0.0))
                    depth = get_float_value(row.get("depth", 0.0))
                    weight = get_string_value(row.get("weight", ""))
                    probes = get_float_value(row.get("probes", 0.0))

                    cns_obj, created = Cns.objects.get_or_create(
                        sample_lib=sample_lib,
                        sequencing_run=sequencing_run,
                        variant_file=variant_file,
                        analysis_run=analysis_run,
                        chromosome=chromosome,
                        start=start,
                        end=end,
                        gene=gene,
                        defaults={
                            "depth": depth,
                            "log2": log2,
                            "weight": weight,
                            "probes": probes,
                        },
                    )

                    if created:
                        created_objects_count += 1
                        stats["successful"] += 1
                    else:
                        update_fields = []
                        for field in optional_fields:
                            if field in row and getattr(cns_obj, field) in (None, 0.0, ""):
                                setattr(cns_obj, field, get_float_value(row[field]))
                                update_fields.append(field)
                        if update_fields:
                            cns_obj.save(update_fields=update_fields)
                            updated_objects_count += 1
                            stats["successful"] += 1

                except Exception as row_err:
                    # Rollback only the failed row (continue processing next)
                    log_and_track_exception("CNS007", f"Row processing failed at index={i}", row_err)
                    stats["failed"] += 1
                    stats["errors"].append(f"Row {i}: {row_err}")
                    continue

        # --- End transaction ---

        stats["created"] = created_objects_count
        stats["updated"] = updated_objects_count

        msg = (
            f"✅ CNS parsing complete for {variant_file.name}: "
            f"Created={created_objects_count}, Updated={updated_objects_count}, "
            f"Total={stats['total_rows']}, Failed={stats['failed']}"
        )
        logger.info(msg)
        return True, msg, stats

    except Exception as e:
        # If any top-level issue happens, rollback entire batch
        error_msg = f"Critical error in parse_cns_file_with_handler for '{file_path}': {str(e)}"
        log_and_track_exception("CNS012", error_msg, e)
        stats["failed"] = stats.get("total_rows", 0)
        stats["errors"].append(error_msg)
        return False, error_msg, stats


def assign_cnv_attachments(analysis_run, file_path):
    """
    Assigns CNV attachment files (diagram.pdf or scatter.png) to all CNS records
    matching the given analysis_run, sequencing_run, and sample_lib.

    Returns:
        (success: bool, message: str, stats: dict)
    """
    logger.info(f"📎 Assigning CNV attachments for file path: {file_path}")

    stats = {
        "total_records": 0,
        "updated_records": 0,
        "failed_records": 0,
        "errors": [],
    }

    try:
        sequencing_run = get_sequencing_run(file_path)
        sample_lib = get_sample_lib(file_path)
        file_name = os.path.basename(file_path).lower()

        queryset = Cns.objects.filter(
            analysis_run=analysis_run,
            sample_lib=sample_lib,
            sequencing_run=sequencing_run,
        )
        stats["total_records"] = queryset.count()

        if stats["total_records"] == 0:
            message = "No matching CNS records found for given analysis run and sample"
            log_and_track_exception("CNA001", message, error_stats=stats)
            return False, message, stats

        updated = 0
        attachment_type = None

        if "diagram" in file_name:
            updated = queryset.update(diagram=file_path)
            attachment_type = "diagram"
        elif "scatter" in file_name:
            updated = queryset.update(scatter=file_path)
            attachment_type = "scatter"
        else:
            message = "No valid attachment found in filename (must contain 'diagram' or 'scatter')"
            log_and_track_exception("CNA002", message, error_stats=stats)
            return False, message, stats

        stats["updated_records"] = updated

        if updated == 0:
            message = f"No CNS records updated — possible data mismatch for {attachment_type}"
            log_and_track_exception("CNA002", message, error_stats=stats)
            return False, message, stats

        message = f"✅ Successfully updated {updated} CNS record(s) with {attachment_type} attachment."
        logger.info(message)
        return True, message, stats

    except Exception as e:
        error_msg = f"Critical error in CNV attachment assignment: {str(e)}"
        log_and_track_exception("CNA001", error_msg, exception_obj=e)
        stats["failed_records"] = stats.get("total_records", 0)
        stats["errors"].append(error_msg)
        return False, error_msg, stats

