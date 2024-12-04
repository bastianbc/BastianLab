import pandas as pd
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from .models import VariantCall, GVariant, CVariant, PVariant
from analysisrun.models import AnalysisRun
from samplelib.models import SampleLib
import re
import os
import logging

logger = logging.getLogger("file")

def check_file(file_path):
    """Check if file exists and is readable"""
    logger.debug(f"Checking file: {file_path}")
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return False, f"File not found: {file_path}"
    if not file_path.endswith('.txt'):
        logger.error(f"Invalid file format for {file_path}. Expected .txt file")
        return False, "Invalid file format. Expected .txt file"
    logger.info(f"File check passed for {file_path}")
    return True, ""

def get_caller(filename):
    logger.debug(f"Extracting caller from filename: {filename}")
    caller_match = re.match(r'.*?(\w+)_Final', filename)
    if not caller_match:
        logger.warning(f"Could not extract caller from filename: {filename}")
        return None
    caller = caller_match.group(1)
    logger.debug(f"Extracted caller: {caller}")
    return caller

def parse_p_var(p_var):
    logger.debug(f"Parsing p_var: {p_var}")
    if not p_var:
        logger.debug("p_var is empty")
        return None, None, None
    match = re.match(r'p\.([A-Za-z])(\d+)([A-Za-z])', p_var)
    if match:
        result = (match.group(1), match.group(2), match.group(3))
        logger.debug(f"Parsed p_var successfully: {result}")
        return result
    logger.warning(f"Failed to parse p_var: {p_var}")
    return None, None, None

def get_log2r():
    """
    Note: We need to write some code for this later
    """
    logger.debug("get_log2r called - returning default value 0.0")
    return 0.0

def get_normal_sample_lib(sample_lib):
    logger.debug(f"Getting normal sample lib for: {sample_lib}")
    try:
        normal_sl = SampleLib.objects.filter(
            na_sl_links__nucacid__na_type='dna',
            na_sl_links__nucacid__area_na_links__area__area_type='normal',
            na_sl_links__nucacid__na_sl_links__sample_lib=sample_lib
        ).exclude(pk=sample_lib.pk).distinct().first()

        if normal_sl:
            logger.info(f"Found normal sample lib: {normal_sl}")
        else:
            logger.info("No normal sample lib found")
        return normal_sl
    except Exception as e:
        logger.error(f"Error getting normal sample lib: {str(e)}")
        return None

def get_hg(filename):
    logger.debug(f"Extracting HG version from filename: {filename}")
    match = re.search(r'\.hg(\d+)_', filename)
    if match:
        assembly = match.group(1)
        logger.debug(f"Found assembly version: {assembly}")
        return assembly
    logger.warning(f"Could not extract HG version from filename: {filename}")
    return None

def get_sample_lib(filename):
    logger.debug(f"Getting sample lib from filename: {filename}")
    match = re.match(r'^[^.]+', filename)
    if match:
        name = match.group(0)
        logger.debug(f"Extracted sample lib name: {name}")
        try:
            sample_lib = SampleLib.objects.get(name=name)
            logger.info(f"Found sample lib: {sample_lib}")
            return sample_lib
        except Exception as e:
            logger.error(f"Error finding sample lib with name {name}: {str(e)}")
            return None
    logger.warning(f"Could not extract sample lib name from filename: {filename}")
    return None

def get_sequencing_run(filename):
    logger.debug(f"Getting sequencing run for filename: {filename}")
    return None

def get_analysis_run(name):
    logger.debug(f"Getting analysis run: {name}")
    try:
        analysis_run = AnalysisRun.objects.get(name=name)
        logger.info(f"Found analysis run: {analysis_run}")
        return analysis_run
    except ObjectDoesNotExist:
        logger.error(f"Analysis run not found: {name}")
        return None

def check_required_fields(row):
    logger.debug("Checking required fields in row")
    required_fields = ['Chr', 'Start', 'End', 'Ref', 'Alt', 'Depth',
                      'Ref_reads', 'Alt_reads', 'AAChange.refGene']

    for field in required_fields:
        if field not in row or pd.isna(row[field]):
            logger.error(f"Required field missing: {field}")
            return False, f"Missing field: {field}"
    logger.debug("All required fields present")
    return True, ""

def create_c_and_p_variants(g_variant, aachange, func, gene_detail):
    logger.debug(f"Creating C and P variants for aachange: {aachange}")
    entries = aachange.split(',')
    for entry in entries:
        try:
            logger.debug(f"Processing entry: {entry}")
            gene, nm_id, exon, c_var, p_var = entry.split(':')

            # Create CVariant instance
            c_variant = CVariant.objects.create(
                g_variant=g_variant,
                gene=gene,
                nm_id=nm_id,
                exon=exon,
                c_var=c_var,
                func=func,
                gene_detail=gene_detail
            )
            logger.info(f"Created CVariant: {c_variant}")

            # Create PVariant instance if p_var is present
            if p_var:
                p_ref, p_pos, p_alt = parse_p_var(p_var)
                if all([p_ref, p_pos, p_alt]):
                    p_variant = PVariant.objects.create(
                        c_variant=c_variant,
                        ref=p_ref,
                        pos=p_pos,
                        alt=p_alt
                    )
                    logger.info(f"Created PVariant: {p_variant}")
                else:
                    logger.warning(f"Skipped PVariant creation due to invalid p_var: {p_var}")
        except Exception as e:
            logger.error(f"Error processing AAChange entry '{entry}': {str(e)}")

@transaction.atomic
def variant_file_parser(file_path, analysis_run_name):
    logger.info(f"Starting variant file parser for {file_path}")
    logger.info(f"Analysis run name: {analysis_run_name}")

    # File check
    is_valid, error_msg = check_file(file_path)
    if not is_valid:
        logger.error(f"File validation failed: {error_msg}")
        return False, error_msg, {}

    try:
        # Read file
        logger.debug("Reading file with pandas")
        df = pd.read_csv(file_path, sep='\t')
        if df.empty:
            logger.error("File is empty")
            return False, "File is empty", {}

        filename = os.path.basename(file_path)
        logger.debug(f"Processing filename: {filename}")

        # Sample library check
        sample_lib = get_sample_lib(filename)
        if not sample_lib:
            logger.error(f"Sample library not found: {filename}")
            return False, f"Sample library not found: {filename}", {}

        analysis_run = get_analysis_run(analysis_run_name)
        if not analysis_run:
            logger.error(f"Analysis run not found: {analysis_run_name}")
            return False, f"Analysis run not found: {analysis_run_name}", {}

        stats = {
            "total_rows": len(df),
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        logger.info(f"Starting to process {stats['total_rows']} rows")

        # Process each row
        for index, row in df.iterrows():
            logger.debug(f"Processing row {index + 1}")
            try:
                # Check required fields
                fields_valid, field_error = check_required_fields(row)
                if not fields_valid:
                    logger.error(f"Row {index + 1}: {field_error}")
                    stats["errors"].append(f"Row {index + 1}: {field_error}")
                    stats["failed"] += 1
                    continue

                # Caller check
                caller = get_caller(filename)
                if not caller:
                    logger.error(f"Row {index + 1}: Could not determine caller")
                    stats["errors"].append(f"Row {index + 1}: Could not determine caller")
                    stats["failed"] += 1
                    continue

                with transaction.atomic():
                    logger.debug(f"Creating VariantCall for row {index + 1}")
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

                    logger.debug(f"Creating GVariant for row {index + 1}")
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

                    logger.debug(f"Creating C and P variants for row {index + 1}")
                    create_c_and_p_variants(
                        g_variant=g_variant,
                        aachange=row['AAChange.refGene'],
                        func=row['Func.refGene'],
                        gene_detail=row.get('GeneDetail.refGene', '')
                    )

                    stats["successful"] += 1
                    logger.info(f"Successfully processed row {index + 1}")

            except Exception as e:
                logger.error(f"Error processing row {index + 1}: {str(e)}", exc_info=True)
                stats["errors"].append(f"Row {index + 1}: {str(e)}")
                stats["failed"] += 1

        # Create result message
        if stats["failed"] == stats["total_rows"]:
            logger.error("No variants could be processed")
            return False, "No variants could be processed", stats
        elif stats["failed"] > 0:
            logger.warning(f"{stats['successful']} variants processed successfully, {stats['failed']} variants failed")
            return True, f"{stats['successful']} variants processed successfully, {stats['failed']} variants failed", stats
        else:
            logger.info("All variants processed successfully")
            return True, "All variants processed successfully", stats

    except Exception as e:
        logger.critical(f"Critical error in variant file parser: {str(e)}", exc_info=True)
        return False, f"Critical error: {str(e)}", {}
