import pandas as pd
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from .models import VariantCall, GVariant, CVariant, PVariant
from analysisrun.models import AnalysisRun
from samplelib.models import SampleLib
import re
import os

def check_file(file_path):
    """Check if file exists and is readable"""
    if not os.path.exists(file_path):
        return False, f"File not found: {file_path}"
    if not file_path.endswith('.txt'):
        return False, "Invalid file format. Expected .txt file"
    return True, ""

def get_caller(filename):
    caller_match = re.match(r'.*?(\w+)_Final', filename)
    if not caller_match:
        return None
    return caller_match.group(1)

def parse_p_var(p_var):
    if not p_var:
        return None, None, None
    match = re.match(r'p\.([A-Za-z])(\d+)([A-Za-z])', p_var)
    if match:
        return match.group(1), match.group(2), match.group(3)
    return None, None, None

def get_sample_lib(filename):
    match = re.match(r'^[^.]+', filename)
    if not match:
        return None
    name = match.group(0)
    try:
        return SampleLib.objects.get(name=name)
    except ObjectDoesNotExist:
        return None

def check_required_fields(row):
    """Check if all required fields exist in row"""
    required_fields = ['Chr', 'Start', 'End', 'Ref', 'Alt', 'Depth',
                      'Ref_reads', 'Alt_reads', 'AAChange.refGene']

    for field in required_fields:
        if field not in row or pd.isna(row[field]):
            return False, f"Missing field: {field}"
    return True, ""

@transaction.atomic
def variant_file_parser(file_path, analysis_run_name):
    """
    Parse variant file and save to database.
    Returns error message if fails.

    Returns:
        tuple: (success, message, statistics)
    """
    # File check
    is_valid, error_msg = check_file(file_path)
    if not is_valid:
        return False, error_msg, {}

    try:
        # Read file
        df = pd.read_csv(file_path, sep='\t')
        if df.empty:
            return False, "File is empty", {}

        filename = os.path.basename(file_path)

        # Sample library check
        sample_lib = get_sample_lib(filename)
        if not sample_lib:
            return False, f"Sample library not found: {filename}", {}

        # Analysis run check
        try:
            analysis_run = get_analysis_run(analysis_run_name)
        except ObjectDoesNotExist:
            return False, f"Analysis run not found: {analysis_run_name}", {}

        stats = {
            "total_rows": len(df),
            "successful": 0,
            "failed": 0,
            "errors": []
        }

        # Process each row
        for index, row in df.iterrows():
            try:
                # Check required fields
                fields_valid, field_error = check_required_fields(row)
                if not fields_valid:
                    stats["errors"].append(f"Row {index + 1}: {field_error}")
                    stats["failed"] += 1
                    continue

                # Caller check
                caller = get_caller(filename)
                if not caller:
                    stats["errors"].append(f"Row {index + 1}: Could not determine caller")
                    stats["failed"] += 1
                    continue

                with transaction.atomic():
                    variant_call = VariantCall.objects.create(
                        analysis_run=analysis_run,
                        sample_lib=sample_lib,
                        sequencing_run=get_sequencing_run(filename),
                        coverage=row['Depth'],
                        log2r=get_log2r(),
                        caller=caller,
                        normal_sl=get_normal_sample_lib(sample_lib),
                        label="",
                        ref_read=row['Ref_reads'],
                        alt_read=row['Alt_reads'],
                    )

                    g_variant = GVariant.objects.create(
                        variant_call=variant_call,
                        hg=get_hg(filename),
                        chrom=row['Chr'],
                        start=row['Start'],
                        end=row['End'],
                        ref=row['Ref'],
                        alt=row['Alt'],
                        avsnp150=row.get('avsnp150', '')
                    )

                    create_c_and_p_variants(
                        g_variant=g_variant,
                        aachange=row['AAChange.refGene'],
                        func=row['Func.refGene'],
                        gene_detail=row.get('GeneDetail.refGene', '')
                    )

                    stats["successful"] += 1

            except Exception as e:
                stats["errors"].append(f"Row {index + 1}: {str(e)}")
                stats["failed"] += 1

        # Create result message
        if stats["failed"] == stats["total_rows"]:
            return False, "No variants could be processed", stats
        elif stats["failed"] > 0:
            return True, f"{stats['successful']} variants processed successfully, {stats['failed']} variants failed", stats
        else:
            return True, "All variants processed successfully", stats

    except Exception as e:
        return False, f"Critical error: {str(e)}", {}
