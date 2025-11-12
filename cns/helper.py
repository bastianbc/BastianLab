import os
import csv
import sys
import base64
from PIL import Image
from io import BytesIO
import logging
import io
import s3fs
import logging
import boto3
from collections import defaultdict

from django.conf import settings
from analysisrun.models import AnalysisRun
from cns.models import Cns
from samplelib.models import SampleLib
from sequencingrun.models import SequencingRun
from analysisrun.models import VariantFile
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import pylab
from urllib.parse import urlparse

logger = logging.getLogger("file")


BASE_PATH = settings.VARIANT_FILES_SOURCE_DIRECTORY

# Global dictionary to hold exception statistics
EXCEPTION_STATS = defaultdict(int)

# --- Exception Codes (for this module) ---
# Format: <FunctionAbbreviation><CodeNumber>
EXCEPTION_CODES = {
    # General CNS codes
    "CNS001": "Folder/Path Error in handle_variant_file",
    "CNS002": "AnalysisRun DoesNotExist",
    "CNS003": "SequencingRun DoesNotExist",
    "CNS004": "SampleLib DoesNotExist",
    "CNS005": "Path/Directory not found (find_folders)",
    "CNS006": "CNS object creation failed (parse_cns_file)",
    "CNS007": "CNS object creation failed (parse_cns_file_with_handler)",
    "CNS008": "Data conversion error (get_float_value)",
    "CNS009": "Error reading CNS file with pandas",
    "CNS010": "Graph generation error",
    "CNS011": "General parsing error (parse_cns_file)",
    "CNS012": "General parsing error (parse_cns_file_with_handler)",
    "CNS013": "File name parsing error (e.g. split)",
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

def handle_variant_file(ar_name, folder):
    folder_path = find_folders(ar_name, folder)
    if folder_path:
        cns_files=find_cns_files(folder_path)
        return cns_files
    else:
        raise Exception("Folder not found")

def find_folders(ar_name, folder):
    first_level_dirs = next(os.walk(BASE_PATH))[1]
    if not any(ar_name in dir_name for dir_name in first_level_dirs):
        raise ValueError(f"Error: '{ar_name}' not found in any first-level directories of {BASE_PATH}")

    return os.path.join(BASE_PATH, ar_name, folder)

def find_cns_files(folder):
    cns_files = []
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith(".cns"):
                cns_files.append(os.path.join(root, file))
    return cns_files

def parse_cns_file(file_path, ar_name):
    print("@@@@@@@@@ parsing cns file", file_path)
    try:
        analysis_run = AnalysisRun.objects.get(name=ar_name)
        file_name = file_path.split['/'][-1]

        created_objects_count = 0

        sample_lib = file_name.split(".")[1]
        sequencing_run = file_name.split(".")[0]
        # with open(file_path, "r") as f:
        #     reader = csv.DictReader(f)
        df = pd.read_csv(file_path, index_col=False, sep='\t')
        for index, row in df.iterrows():
            # Check if the Cns object already exists
            if not Cns.objects.filter(
                sample_lib=sample_lib,
                sequencing_run=sequencing_run,
                variant_file=file_path,
                analysis_run=analysis_run,
                chromosome=row["chromosome"],
                start=int(row["start"]),
                end=int(row["end"]),
            ).exists():

                def get_float_value(value, default=0.0):
                    try:
                        return float(value)
                    except ValueError:
                        return default

                depth = get_float_value(row["depth"])
                ci_hi = get_float_value(row["ci_hi"])
                ci_lo = get_float_value(row["ci_lo"])
                cn = get_float_value(row.get("cn", 0.0))
                log2 = get_float_value(row["log2"])
                p_bintest = get_float_value(row.get("p_bintest", 0.0))
                p_ttest = get_float_value(row.get("p_ttest", 0.0))
                probes = get_float_value(row["probes"])
                weight = get_float_value(row["weight"])

                Cns.objects.create(
                    sample_lib=sample_lib,
                    sequencing_run=sequencing_run,
                    variant_file=file_path,
                    analysis_run=analysis_run,
                    chromosome=row["chromosome"],
                    start=int(row["start"]),
                    end=int(row["end"]),
                    gene=row["gene"],
                    depth=depth,
                    ci_hi=ci_hi,
                    ci_lo=ci_lo,
                    cn=cn,
                    log2=log2,
                    p_bintest=p_bintest,
                    p_ttest=p_ttest,
                    probes=probes,
                    weight=weight,
                )

                created_objects_count += 1

        return created_objects_count
    except AnalysisRun.DoesNotExist:
        print(f"AnalysisRun with name {ar_name} does not exist")
    except Exception as e:
        print(f"Error parsing file: {e}")

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
    file_name = file_path.split("/")[-1]
    sequencing_run_name = file_name.split(".")[0]
    try:
        return SequencingRun.objects.get(name=sequencing_run_name)
    except SequencingRun.DoesNotExist:
        logger.error(f"Sequencing run not found: {sequencing_run_name}")
        return None

def get_sample_lib(file_path):
    file_name = file_path.split("/")[-1]
    sample_lib_name = file_name.split(".")[1]
    try:
        return SampleLib.objects.get(name=sample_lib_name)
    except SampleLib.DoesNotExist:
        logger.error(f"Sample library not found: {sample_lib_name}")
        return None

def read_cns_file(file_path):
    """
    Reads a CNS (Copy Number Segment) file from S3 or local disk into a pandas DataFrame.
    Automatically converts HTTPS S3 URLs to s3:// format.
    Skips non-text (PDF/PNG) attachments.
    """
    logger.info(f"Reading CNS file: {file_path}")

    # --- Step 0: Early skip for attachments ---
    if file_path.endswith((".pdf", ".png")):
        logger.warning(f"Skipping attachment (not a CNS text file): {file_path}")
        return None

    fs = s3fs.S3FileSystem(anon=False)

    # --- Step 1: Normalize path into S3 or local format ---
    s3_path = file_path
    if file_path.startswith("https://s3."):
        # convert "https://s3.us-west-2.amazonaws.com/bucket/key" → "s3://bucket/key"
        parsed = urlparse(file_path)
        bucket = parsed.netloc.split(".")[-3] if parsed.netloc.startswith("s3") else parsed.netloc
        # e.g. netloc: s3.us-west-2.amazonaws.com → bucket = "bastian-lab..."
        if parsed.netloc.endswith("amazonaws.com"):
            bucket_and_key = parsed.path.lstrip("/").split("/", 1)
            if len(bucket_and_key) == 2:
                bucket, key = bucket_and_key
                s3_path = f"s3://{bucket}/{key}"
        logger.debug(f"Converted HTTPS URL to S3 path: {s3_path}")

    elif file_path.startswith(("http://", "https://")):
        # generic HTTP path (not S3)
        parsed = urlparse(file_path)
        bucket_and_key = parsed.path.lstrip("/").split("/", 1)
        if len(bucket_and_key) == 2:
            bucket, key = bucket_and_key
            s3_path = f"s3://{bucket}/{key}"
        logger.debug(f"Converted generic HTTP URL to S3 path: {s3_path}")

    # --- Step 2: Read content ---
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
        logger.error(f"❌ Failed to read {file_path}: {e}", exc_info=True)
        raise

    # --- Step 3: Parse TSV content ---
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
            row += [''] * (header_count - len(row))
        elif len(row) > header_count:
            row = row[:header_count]
        data.append(row)

    if len(data) < 2:
        raise ValueError(f"No valid data rows found in CNS file: {file_path}")

    df = pd.DataFrame(data[1:], columns=data[0])
    logger.info(f"✅ Parsed CNS file successfully — {len(df)} rows, {len(df.columns)} columns.")
    return df.head(1)



def get_float_value(value, default=0.0):
    """Safely convert value to float with default fallback"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def get_string_value(value, default=""):
    """Safely convert value to string with default fallback"""
    try:
        return str(value) if value is not None else default
    except:
        return default

def get_or_none(model_class, **kwargs):
    try:
        return model_class.objects.get(**kwargs)
    except Exception as e:
        return None

def parse_cns_file_with_handler(file_path, analysis_run, variant_file):
    """
    Parse and register CNS files (.cns, .call.cns, .bintest.cns).
    Creates or updates Cns objects based on genomic coordinates.
    Fills missing columns if records already exist.
    """

    logger.info(f"🧬 Starting variant file parser for {variant_file.name}")
    print(f"$$$$$$$$$$ Parsing CNS file: {variant_file}")
    print(file_path)

    sequencing_run = get_sequencing_run(file_path)
    sample_lib = get_sample_lib(file_path)

    # Read file
    df = read_cns_file(file_path)
    df.columns = [c.strip().lower() for c in df.columns]

    created_objects_count = 0
    updated_objects_count = 0
    core_fields = ['chromosome', 'start', 'end', 'gene', 'log2', 'depth', 'weight', 'probes']
    optional_fields = ['ci_hi', 'ci_lo', 'cn', 'p_bintest', 'p_ttest']

    for i, row in df.iterrows():
        chromosome = row.get("chromosome")
        start = int(row.get("start", 0))
        end = int(row.get("end", 0))
        gene = get_string_value(row.get("gene", ""))
        log2 = get_float_value(row.get("log2", 0.0))
        depth = get_float_value(row.get("depth", 0.0))
        weight = get_string_value(row.get("weight", ""))
        probes = get_float_value(row.get("probes", 0.0))

        # Try to find an existing CNS record
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
        print(i)
        # If already exists, fill missing optional fields
        if not created:
            updated = False
            for field in optional_fields:
                if field in row and getattr(cns_obj, field) in (None, 0.0, ""):
                    setattr(cns_obj, field, get_float_value(row[field]))
                    updated = True
            if updated:
                cns_obj.save(update_fields=optional_fields)
                updated_objects_count += 1
        else:
            # Set optional fields if they exist in current file
            for field in optional_fields:
                if field in row:
                    setattr(cns_obj, field, get_float_value(row[field]))
            cns_obj.save()
            created_objects_count += 1

    msg = (
        f"✅ CNS parsing complete for {variant_file.name}: "
        f"Created={created_objects_count}, Updated={updated_objects_count}"
    )
    logger.info(msg)
    print(msg)

    return True, msg


def assign_cnv_attachments(analysis_run, file_path):
    """
    Assigns CNV attachment files (diagram.pdf, scatter.png) to all CNS records
    matching the given analysis_run, sequencing_run, and sample_lib.

    Returns:
        (success: bool, message: str, stats: dict)
    """
    print(f"📎 Assigning CNV attachments for file path: {file_path}")
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

        diagram_path, scatter_path = (
            (file_path, None) if "diagram" in os.path.basename(file_path).lower()
            else (None, file_path) if "scatter" in os.path.basename(file_path).lower()
            else (None, None)
        )

        logger.debug(f"Found diagram: {diagram_path or 'None'} | scatter: {scatter_path or 'None'}")

        # --- Filter target CNS records ---
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

        # --- Perform update ---
        updated = queryset.update(
            diagram=diagram_path,
            scatter=scatter_path,
        )
        stats["updated_records"] = updated

        # --- Evaluate outcome ---
        if updated == 0:
            message = "No CNS records updated — attachments may be missing"
            logger.warning(message)
            return False, message, stats

        if not (diagram_path or scatter_path):
            message = f"{updated} CNS record(s) updated, but no attachments found in S3"
            logger.warning(message)
            return True, message, stats

        message = (
            f"✅ Successfully updated {updated} CNS record(s) "
            f"(diagram={'yes' if diagram_path else 'no'}, scatter={'yes' if scatter_path else 'no'})"
        )
        logger.info(message)
        return True, message, stats

    except Exception as e:
        error_msg = f"Critical error in CNV attachment assignment: {str(e)}"
        log_and_track_exception("CNA001", error_msg, exception_obj=e)
        stats["failed_records"] = stats.get("total_records", 0)
        stats["errors"].append(error_msg)
        return False, error_msg, stats

