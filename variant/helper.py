import re
import os
import logging
import boto3
import csv
import sys
import s3fs
import io

import pandas as pd
# from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from sequencingrun.models import SequencingRun
from .models import VariantCall, GVariant, CVariant, PVariant
from gene.models import Gene
from analysisrun.models import AnalysisRun, VariantFile
from samplelib.models import SampleLib
from urllib.parse import urlparse


logger = logging.getLogger("file")


def check_file(file_path):
    """Check if file exists and is readable (supports local + fixed S3 URL format)."""
    logger.debug(f"Checking file: {file_path}")
    if file_path.startswith("http"):
        parsed = urlparse(file_path)
        # Always of the form: https://s3.us-west-2.amazonaws.com/<bucket>/<key>
        parts = parsed.path.lstrip("/").split("/", 1)
        if len(parts) < 2:
            logger.error(f"Invalid S3 URL format: {file_path}")
            return False, "Invalid S3 URL format"

        bucket, key = parts[0], parts[1]
        s3 = boto3.client("s3")

        logger.debug(f"Parsed bucket: {bucket}")
        logger.debug(f"Parsed key: {key}")

        try:
            s3.head_object(Bucket=bucket, Key=key)
            logger.info(f"S3 file check passed for {file_path}")
            return True, ""
        except s3.exceptions.ClientError as e:
            code = e.response["Error"]["Code"]
            msg = e.response["Error"]["Message"]
            logger.error(f"S3 check failed ({code}): {msg}")
            return False, f"S3 error {code}: {msg}"

    # Local file check
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return False, f"File not found: {file_path}"

    if not file_path.endswith(".txt"):
        logger.error(f"Invalid file format for {file_path}. Expected .txt file")
        return False, "Invalid file format. Expected .txt file"

    logger.info(f"Local file check passed for {file_path}")
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
    if "M1?" in p_var:
        start, end, reference_residues, inserted_residues, change_type = (1, 1, "M", "", "substitution")
        return start, end, reference_residues, inserted_residues, change_type

    # Handle frames shift mutations
    if "fs" in p_var:
        start, end, reference_residues, inserted_residues, change_type = (0, 0, "", "", "fs")
        return start, end, reference_residues, inserted_residues, change_type

    # Handle special case: p.*92* (termination codon to termination codon)
    match_term_to_term = re.match(r'p\.\*(\d+)\*', p_var)
    if match_term_to_term:
        start, end, reference_residues, inserted_residues, change_type = (
            match_term_to_term.group(1),
            match_term_to_term.group(1),
            "*",
            "*",
            "synonymous"  # or you could use "substitution" if preferred
        )
        logger.debug(f"Parsed p_var successfully: {start, end, reference_residues, inserted_residues, change_type}")
        return start, end, reference_residues, inserted_residues, change_type

    # Handle mutations at termination codon with delins (e.g., p.*360delinsLIVPPRHPPCPSLVGY*)
    match_term_delins = re.match(r'p\.\*(\d+)delins([A-Z]+)\*?', p_var)
    if match_term_delins:
        start, end, reference_residues, inserted_residues, change_type = (
            match_term_delins.group(1),
            match_term_delins.group(1),
            "*",
            match_term_delins.group(2) + ("*" if p_var.endswith("*") else ""),
            "delins"
        )
        logger.debug(f"Parsed p_var successfully: {start, end, reference_residues, inserted_residues, change_type}")
        return start, end, reference_residues, inserted_residues, change_type

    # Handle standard substitution
    match = re.match(r'p\.([A-Z])(\d+)([A-Z])', p_var)
    if match:
        start, end, reference_residues, inserted_residues, change_type = (
            match.group(2),
            match.group(2),
            match.group(1),
            match.group(3),
            "substitution"
        )
        logger.debug(f"Parsed p_var successfully: {start, end, reference_residues, inserted_residues, change_type}")
        return start, end, reference_residues, inserted_residues, change_type

    # Handle single position variants
    match2 = re.match(r'p\.([A-Z])(\d+)(delins|del|ins)', p_var)
    if match2:
        start, end, reference_residues, inserted_residues, change_type = (
            match2.group(2),
            match2.group(2),
            match2.group(1),
            "",
            match2.group(3)
        )
        logger.debug(f"Parsed p_var successfully: {start, end, reference_residues, inserted_residues, change_type}")
        return start, end, reference_residues, inserted_residues, change_type

    # Handle nonsense mutations
    match3 = re.match(r'p\.([A-Z])(\d+)\*', p_var)
    if match3:
        start, end, reference_residues, inserted_residues, change_type = (
            match3.group(2),
            match3.group(2),
            match3.group(1),
            "*",
            "nonsense"
        )
        logger.debug(f"Parsed p_var successfully: {start, end, reference_residues, inserted_residues, change_type}")
        return start, end, reference_residues, inserted_residues, change_type

    m_num = re.match(r"^p\.(\d+)_(\d+)(delins|del|ins)\*?$", p_var)
    if m_num:
        start = m_num.group(1)
        end = m_num.group(2)
        change_type = m_num.group(3)
        # no reference residues or inserted residues
        return start, end, "", "", change_type

    # Handle more complex variants
    match_range = re.match(
        r"^p\.([A-Z])(\d+)_([A-Z]?)(\d+)"  # ref‐AA1, pos1, optional ref‐AA2, pos2
        r"(delins|del|ins)"  # change type
        r"([A-Z]*)\*?$",  # *optional* inserted‐residues + optional '*'
        p_var
    )
    if match_range:
        start = match_range.group(2)
        end = match_range.group(4)
        # if the second-letter was missing, just use the first
        ref1 = match_range.group(1)
        ref2 = match_range.group(3) or ref1
        reference_residues = ref1 + ref2

        change_type = match_range.group(5)
        inserted_residues = match_range.group(6)
        # re-attach trailing * if needed
        if p_var.endswith("*") and not inserted_residues.endswith("*"):
            inserted_residues += "*"

        logger.debug("match_range Parsed p_var successfully:",
              start, end, reference_residues,
              inserted_residues, change_type)
        return start, end, reference_residues, inserted_residues, change_type

    logger.warning(f"Failed to parse p_var: {p_var}")
    return None, None, None, None, None

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
            na_sl_links__nucacid__area_na_links__area__area_type__value='normal',
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
    sample_lib_name = filename.split('.')[1]
    try:
        sample_lib = SampleLib.objects.get(name=sample_lib_name)
        return sample_lib
    except SampleLib.DoesNotExist:
        logger.error(f"Sample library not found: {sample_lib_name}")
        return None

def get_sequencing_run(filename):
    logger.debug(f"Getting sequencing run for filename: {filename}")
    sequencing_run_name = filename.split('.')[0]
    try:
        sequencing_run = SequencingRun.objects.get(name=sequencing_run_name)
        return sequencing_run
    except SequencingRun.DoesNotExist:
        logger.error(f"Sequencing run not found: {sequencing_run_name}")
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

def get_gene(gene_name, hg):
    logger.debug(f"Getting gene: {gene_name} for hg: {hg}")
    try:
        gene = Gene.objects.get(name=gene_name, hg=hg)
        return gene
    except Gene.DoesNotExist:
        logger.error(f"Gene not found: {gene_name}")
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

def get_or_create_g_variant(hg, chrom, start, end, ref, alt, avsnp150):
    """
    Get or create GVariant based on unique genomic coordinates.
    Reuses existing GVariant if one with same chrom, start, end, ref, alt exists.
    """
    logger.debug(f"Getting or creating GVariant for {chrom}:{start}-{end} {ref}>{alt}")

    try:
        # Try to get existing GVariant with same coordinates
        g_variant = GVariant.objects.get(
            chrom=chrom,
            start=start,
            end=end,
            ref=ref,
            alt=alt
        )
        logger.info(f"Found existing GVariant: {g_variant.start}-{g_variant.end}-{g_variant.ref} {g_variant.alt}")
        return g_variant
    except GVariant.DoesNotExist:
        # Create new GVariant if none exists
        g_variant = GVariant.objects.create(
            hg=hg,
            chrom=chrom,
            start=start,
            end=end,
            ref=ref,
            alt=alt,
            avsnp150=avsnp150
        )
        logger.info(f"Created new GVariant:{g_variant.start}-{g_variant.end}-{g_variant.ref} {g_variant.alt}")
        return g_variant

def create_gene_detail(gene_detail, row_gene, g_variant, func, filename):
    entries = gene_detail.split(';')
    alias_meta, variant_meta = [], []
    for entry in entries:
        # try:
            logger.debug(f"Processing gene_detail: {entry}")
            nm_id, exon, c_var = entry.split(':')
            # AnalysisRun.objects.get() TODO hg is getting from Analysis Run
            hg_value = f"hg{get_hg(filename)}"
            gene_obj = get_gene(row_gene, hg_value)
            # Create CVariant instance
            is_alias = True if nm_id.lower() == gene_obj.nm_canonical.lower() else False
            if gene_obj:
                c_variant = CVariant.objects.create(
                    g_variant=g_variant,
                    gene=gene_obj,
                    nm_id=nm_id,
                    exon=exon,
                    c_var=c_var[:99],
                    func=func,
                    gene_detail=entry[:99],
                    is_alias=is_alias,
                    is_gene_detail=True
                )
                (variant_meta if is_alias else alias_meta).append(entry)
                logger.info(f"Created CVariant: {c_variant}")
        # except Exception as e:
        #     logger.error(f"Error processing gene_detail entry '{entry}': {str(e)}")

    list(set(alias_meta)), list(set(variant_meta))
    variant_meta = ", ".join(variant_meta)
    alias_meta = ", ".join(alias_meta)
    return alias_meta, variant_meta



def create_c_and_p_variants(g_variant, variant_call, aachange, func, gene_detail, filename, row_gene):
    logger.debug(f"Creating C and P variants for aachange: {aachange}")
    entries = aachange.split(',')
    # Handle "UNKNOWN" or "." cases first
    if any(aachange.strip() == invalid for invalid in ["UNKNOWN", "."]):
        if gene_detail.strip() == "." or "dist=" in gene_detail:
            return
        alias_meta, variant_meta = create_gene_detail(gene_detail, row_gene, g_variant, func, filename)
        variant_call.variant_meta = variant_meta
        variant_call.alias_meta = alias_meta
        variant_call.save()
        return

    alias_meta, variant_meta = [], []
    # Process valid entries
    for entry in entries:
        # try:
        parts = entry.split(':')
        if len(parts) not in [4, 5]:
            logger.warning(f"Skipping malformed entry: {entry}")
            continue

        gene, nm_id, exon, c_var = parts[:4]
        p_var = parts[-1] if len(parts) == 5 else None

        # Fetch gene safely
        hg_value = f"hg{get_hg(filename)}"
        gene_obj = get_gene(gene, hg_value)
        if not gene_obj:
            logger.warning(f"Gene not found for entry: {entry}")
            continue

        # Determine alias relationship
        is_alias = nm_id.lower() == gene_obj.nm_canonical.lower()
        # Create CVariant
        c_variant = CVariant.objects.create(
            g_variant=g_variant,
            gene=gene_obj,
            nm_id=nm_id,
            exon=exon,
            c_var=c_var[:99],
            func=func,
            gene_detail=entry[:99],
            is_alias=is_alias,
        )
        logger.info(f"Created CVariant: {c_variant.gene_detail}")

        # Create PVariant if present
        if p_var:
            start, end, ref_res, ins_res, change_type = parse_p_var(p_var)
            ins_res = f"{ins_res[:98]}*" if p_var.endswith("*") else ins_res[:99]

            p_variant = PVariant.objects.create(
                c_variant=c_variant,
                start=start,
                end=end,
                reference_residues=ref_res,
                inserted_residues=ins_res,
                change_type=change_type,
                name_meta=p_var[:99],
                is_alias=is_alias,
            )
            (variant_meta if is_alias else alias_meta).append(f'{p_variant.name_meta}({c_variant.nm_id})')
            logger.info(f"Created PVariant: {p_variant.id}-{p_variant.start}-{p_variant.end}-{p_variant.name_meta}-")
    alias_meta, variant_meta = list(set(alias_meta)), list(set(variant_meta))
    variant_meta = ", ".join(variant_meta)
    alias_meta = ", ".join(alias_meta)
    variant_call.variant_meta = variant_meta
    variant_call.alias_meta = alias_meta
    variant_call.save()
    logger.info(f"Varaint Call Alias : {variant_call.alias_meta} - Varaint Call Variant : {variant_call.variant_meta}")
    # except Exception as e:
    #     logger.error(f"Error processing AAChange entry '{entry}': {str(e)}", exc_info=True)


def read_csv_file_custom(file_path):
    """
    Reads a TSV/CSV file from either local disk or S3 (HTTPS-style path).
    Ensures consistent number of columns by padding/truncating.
    """

    # Handle URLs like:
    # https://s3.us-west-2.amazonaws.com/<bucket>/<key>
    if file_path.startswith("http"):
        parsed = urlparse(file_path)
        path_parts = parsed.path.lstrip("/").split("/", 1)
        if len(path_parts) < 2:
            raise ValueError(f"Invalid S3 URL format: {file_path}")

        bucket, key = path_parts
        s3_path = f"s3://{bucket}/{key}"
        fs = s3fs.S3FileSystem(anon=False)
        with fs.open(s3_path, "r") as f:
            content = f.read()

    else:
        with open(file_path, "r") as f:
            content = f.read()

    # Parse content as TSV
    lines = content.strip().split("\n")
    headers = lines[0].split("\t")
    header_count = len(headers)
    csv.field_size_limit(min(sys.maxsize, 2147483647))

    data = []
    reader = csv.reader(io.StringIO(content), delimiter="\t")
    for i, row in enumerate(reader):
        if i == 0:
            headers = row
            data.append(row)
        else:
            # pad/truncate to keep consistent columns
            if len(row) < header_count:
                row += [''] * (header_count - len(row))
            elif len(row) > header_count:
                row = row[:header_count]
            data.append(row)

    df = pd.DataFrame(data[1:], columns=data[0])
    return df.head(5)  # TODO: remove this line limit after testing


# @transaction.atomic
def variant_file_parser(file_path, analysis_run, variant_file):
    logger.info(f"Starting variant file parser for {file_path}")
    logger.info(f"Analysis run name: {analysis_run}")
    # File check
    is_valid, error_msg = check_file(file_path)
    if not is_valid:
        logger.error(f"File validation failed: {error_msg}")
        return False, error_msg, {}

    # try:
    # Read file
    logger.debug("Reading file with pandas")
    df = read_csv_file_custom(file_path)
    df = df.reset_index(drop=True)

    if df.empty:
        logger.error("File is empty")
        return False, "File is empty", {}

    filename = file_path.split("/")[-1]

    logger.debug(f"Processing filename: {filename}")

    # Sample library check
    sample_lib = get_sample_lib(filename)
    if not sample_lib:
        logger.error(f"Sample library not found: {filename}")
        return False, f"Sample library not found: {filename}", {}


    stats = {
        "total_rows": len(df),
        "successful": 0,
        "failed": 0,
        "errors": []
    }
    logger.info(f"Starting to process {stats['total_rows']} rows")

    # Process each row
    for index, row in df.iterrows():
        # try:
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

        # with transaction.atomic(): # todo uncomment this
        logger.debug(f"Getting or creating GVariant for row {index + 1}")

        g_variant = get_or_create_g_variant(
            hg=get_hg(filename),
            chrom=row['Chr'],
            start=row['Start'],
            end=row['End'],
            ref=row['Ref'],
            alt=row['Alt'],
            avsnp150=row.get('avsnp150', '')
        )

        variant_call = VariantCall.objects.create(
            analysis_run=analysis_run,
            sample_lib=sample_lib,
            sequencing_run=get_sequencing_run(filename),
            variant_file=variant_file,
            g_variant=g_variant,
            coverage=row['Depth'],
            log2r=get_log2r(),
            caller=caller,
            normal_sl=get_normal_sample_lib(sample_lib),
            label="",
            ref_read=row['Ref_reads'],
            alt_read=row['Alt_reads'],
        )
        logger.info(f"Created variant_call {variant_call.id}-{variant_call.caller}-{variant_call.ref_read}-{variant_call.alt_read}")
        stats["successful"] += 1

        create_c_and_p_variants(
            g_variant=g_variant,
            variant_call=variant_call,
            aachange=row['AAChange.refGene'],
            func=row['ExonicFunc.refGene'],
            gene_detail=row.get('GeneDetail.refGene', ''),
            filename=filename,
            row_gene=row['Gene.refGene']
        )

            # generate_variant_meta_alias_meta(variant_call)

        # except Exception as e:
        #     logger.error(f"Error processing row {index + 1}: {str(e)}", exc_info=True)
        #     stats["errors"].append(f"Row {index + 1}: {str(e)}")
        #     stats["failed"] += 1

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

    # except Exception as e:
    #     logger.critical(f"Critical error in variant file parser: {str(e)}", exc_info=True)
    #     return False, f"Critical error: {str(e)}", {}

