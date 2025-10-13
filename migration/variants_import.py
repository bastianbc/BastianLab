import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test1.settings")
django.setup()
from sequencingrun.models import SequencingRun
from django.conf import settings
import pandas as pd
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from variant.models import VariantCall, GVariant, CVariant, PVariant, VariantFile
from analysisrun.models import AnalysisRun
from samplelib.models import SampleLib
import re
import logging
from pathlib import Path
from gene.models import Gene
import csv
import sys

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
    match = re.match(r'^[^.]+\.([A-Za-z0-9-]+)\.', filename)
    if match:
        name = match.group(1)
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
    match = re.match(r'^[^.]+', filename)
    if match:
        name = match.group(0)
        logger.debug(f"Extracted sequencing name: {name}")
        try:
            seq_run = SequencingRun.objects.get(name=name)
            logger.info(f"Found sample lib: {seq_run}")
            return seq_run
        except Exception as e:
            logger.error(f"Error finding sequencing with name {name}: {str(e)}")
            return None
    logger.warning(f"Could not extract sequencing name from filename: {filename}")
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

def get_variant_file(file_path):
    logger.debug(f"Getting variant file: {file_path}")
    try:
        variant_file = VariantFile.objects.get(name=file_path.split("/")[-1])
        logger.info(f"Found variant file: {variant_file}")
        return variant_file
    except ObjectDoesNotExist:
        logger.error(f"Variant file not found: {file_path}")
        return None

def get_gene(name, hg, canonical):
    logger.debug(f"Getting gene: {name}")
    try:
        if "MUC1" in name or "MUC2" in name:
            gene = Gene.objects.get(name__icontains=name, hg=hg, nm_canonical=canonical)
            return gene
        gene = Gene.objects.get(name=name, hg=hg)
        logger.info(f"Found gene: {name}")
        return gene
    except ObjectDoesNotExist:
        logger.error(f"Gene not found: {name}, with nm_canonical: {canonical}")
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

def create_gene_detail(gene_detail, row_gene, g_variant, func):
    entries = gene_detail.split(';')
    for entry in entries:
        try:
            logger.debug(f"Processing gene_detail: {entry}")
            nm_id, exon, c_var = entry.split(':')
            # AnalysisRun.objects.get() TODO hg is getting from Analysis Run
            gene = get_gene(row_gene, "hg38", nm_id)
            # Create CVariant instance
            is_alias = True if nm_id.lower() == gene.nm_canonical.lower() else False
            if gene:
                c_variant = CVariant.objects.create(
                    g_variant=g_variant,
                    gene=gene,
                    nm_id=nm_id,
                    exon=exon,
                    c_var=c_var,
                    func=func,
                    gene_detail=entry[:99],
                    is_alias=is_alias,
                    is_gene_detail=True,
                )
                logger.info(f"Created CVariant: {c_variant}")
        except Exception as e:
            logger.error(f"Error processing gene_detail entry '{entry}': {str(e)}")


def create_c_and_p_variants(g_variant, aachange, func, gene_detail, filename, row_gene):
    logger.debug(f"Creating C and P variants for aachange: {aachange}")
    entries = aachange.split(',')
    if any(aachange.strip() in invalid for invalid in ["UNKNOWN", "."]):
        if gene_detail.strip() == "." or "dist=" in gene_detail:
            return
        create_gene_detail(gene_detail, row_gene, g_variant, func)
    else:
        for entry in entries:
            try:
                logger.debug(f"Processing entry: {entry}")
                if len(entry.split(':'))==4:
                    gene, nm_id, exon, c_var = entry.split(':') # NTRK1:NM_001012331:exon16:c.C2253A:p.Y751X,NTRK1
                    gene = get_gene(gene, "hg38", nm_id) # TODO look at it
                    # Create CVariant instance
                    is_alias = True if nm_id.lower() == gene.nm_canonical.lower() else False
                    if gene:
                        c_variant = CVariant.objects.create(
                            g_variant=g_variant,
                            gene=gene,
                            nm_id=nm_id,
                            exon=exon,
                            c_var=c_var[:99],
                            func=func,
                            gene_detail=entry[:99]
                        )
                        logger.info(f"Created CVariant: {c_variant}")

                if len(entry.split(':'))==5:
                    gene, nm_id, exon, c_var, p_var = entry.split(':') # NTRK1:NM_001012331:exon16:c.C2253A:p.Y751X,NTRK1
                    gene = get_gene(gene, "hg38", nm_id) # TODO look at it
                    # Create CVariant instance
                    is_alias = True if nm_id.lower() == gene.nm_canonical.lower() else False
                    if gene:
                        c_variant = CVariant.objects.create(
                            g_variant=g_variant,
                            gene=gene,
                            nm_id=nm_id,
                            exon=exon,
                            c_var=c_var[:99],
                            func=func,
                            gene_detail=entry[:99],
                            is_alias=is_alias
                        )
                        logger.info(f"Created CVariant: {c_variant}")

                        # Create PVariant instance if p_var is present
                        if p_var:
                            start, end, reference_residues, inserted_residues, change_type = parse_p_var(p_var)
                            inserted_residues = f"{inserted_residues[:98]}*" if p_var.endswith("*") else inserted_residues[:99]
                            p_variant = PVariant.objects.create(
                                c_variant=c_variant,
                                start=start,
                                end=end,
                                reference_residues=reference_residues,
                                inserted_residues=inserted_residues,
                                change_type=change_type,
                                name_meta=p_var[:99],
                                is_alias=is_alias
                            )

            except Exception as e:
                logger.error(f"Error processing AAChange entry '{entry}': {str(e)}")

def read_csv_file_custom(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    # Process content to get headers
    lines = content.strip().split('\n')
    headers = lines[0].split('\t')
    header_count = len(headers)
    csv.field_size_limit(min(sys.maxsize, 2147483647))

    # Read line by line ensuring we get the right number of columns
    data = []
    with open(file_path, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        for i, row in enumerate(reader):
            if i == 0:  # This is the header row
                headers = row
                data.append(row)
            else:
                # Ensure each row has exactly the number of columns we expect
                if len(row) < header_count:
                    # Pad with empty strings if needed
                    row = row + [''] * (header_count - len(row))
                elif len(row) > header_count:
                    # Truncate if too many
                    row = row[:header_count]
                data.append(row)

    # Create DataFrame
    df = pd.DataFrame(data[1:], columns=data[0])
    return df


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
        df = read_csv_file_custom(file_path)
        df = df.reset_index(drop=True)

        if df.empty:
            logger.error(f"File is empty {file_path}")
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

        variant_file = get_variant_file(file_path)
        if variant_file.call:
            return

        if not variant_file:
            logger.error(f"Variant file not found: {file_path}")
            return False, f"Variant file not found: {file_path}", {}

        stats = {
            "total_rows": len(df),
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        logger.info(f"Starting to process {stats['total_rows']} rows")

        # Process each row
        for i, (_, row) in enumerate(df.iterrows(), start=1):
            logger.debug(f"Processing row {i + 1}")
            try:
                # Check required fields
                fields_valid, field_error = check_required_fields(row)
                if not fields_valid:
                    logger.error(f"Row {i + 1}: {field_error}")
                    stats["errors"].append(f"Row {i + 1}: {field_error}")
                    stats["failed"] += 1
                    continue

                # Caller check
                caller = get_caller(filename)
                if not caller:
                    logger.error(f"Row {i + 1}: Could not determine caller")
                    stats["errors"].append(f"Row {i + 1}: Could not determine caller")
                    stats["failed"] += 1
                    continue


                logger.debug(f"Creating VariantCall for row {i + 1}")
                variant_call = VariantCall.objects.create(
                    analysis_run=analysis_run,
                    sample_lib=sample_lib,
                    sequencing_run=get_sequencing_run(filename),
                    variant_file=variant_file,
                    coverage=int(int(row['Ref_reads'])+int(row['Alt_reads'])),
                    log2r=get_log2r(),
                    caller=caller,
                    normal_sl=get_normal_sample_lib(sample_lib),
                    label="",
                    ref_read=row['Ref_reads'],
                    alt_read=row['Alt_reads'],
                )

                logger.debug(f"Creating GVariant for row {i + 1}")
                g_variant = GVariant.objects.create(
                    variant_call=variant_call,
                    hg=get_hg(filename),
                    chrom=row['Chr'],
                    start=row['Start'],
                    end=row['End'],
                    ref=row['Ref'][:99],
                    alt=row['Alt'][:99],
                    avsnp150=row.get('avsnp150', '')
                )

                logger.debug(f"Creating C and P variants for row {i + 1}")
                create_c_and_p_variants(
                    g_variant=g_variant,
                    aachange=row['AAChange.refGene'],
                    func=row['Func.refGene'],
                    gene_detail=row.get('GeneDetail.refGene', ''),
                    filename = filename,
                    row_gene=row['Gene.refGene']
                )

                stats["successful"] += 1
                logger.info(f"Successfully processed row {i + 1}")

            except Exception as e:
                logger.error(f"Error processing row {i + 1}: {str(e)}", exc_info=True)
                stats["errors"].append(f"Row {i + 1}: {str(e)}")
                stats["failed"] += 1



        # Create result message
        if stats["failed"] == stats["total_rows"]:
            logger.error("No variants could be processed")
            return False, "No variants could be processed", stats
        elif stats["failed"] > 0:
            variant_file.call = True
            variant_file.save()
            logger.warning(f"{stats['successful']} variants processed successfully, {stats['failed']} variants failed")
            return True, f"{stats['successful']} variants processed successfully, {stats['failed']} variants failed", stats
        else:
            variant_file.call = True
            variant_file.save()
            logger.info("All variants processed successfully")
            return True, "All variants processed successfully", stats

    except Exception as e:
        logger.critical(f"Critical error in variant file parser: {str(e)}", exc_info=True)
        return False, f"Critical error: {str(e)}", {}

def create_variant_file(row):
    VariantFile.objects.get_or_create(name=row['File'], directory=row['Dir'])

# Parse and save data into the database
def import_variants():
    print("1"*30)
    VariantFile.objects.filter().update(call=False)
    print("2"*30)
    files = VariantFile.objects.filter(name__icontains="hg38", type="variant", variant_calls__isnull=True)
    print("3"*30)
    # VariantCall.objects.filter().delete()
    print("4"*30)
    for file in files:
        file_path = os.path.join(settings.SMB_DIRECTORY_SEQUENCINGDATA,file.directory)
        if "_Filtered" in os.path.join(file_path, file.name):
            variant_file_parser(os.path.join(file_path,file.name), "AR_ALL")


def create_genes(row):
    gene = Gene.objects.create(
        gene_id = row['gene_id'],
        name = row['name'],
        full_name = row['full_name'],
        chr = str(row['chr']),
        start = int(row['start']) if not pd.isnull(row['start']) else 0,
        end = int(row['end']) if not pd.isnull(row['end']) else 0,
        hg = row['Hg'],
        nm_canonical = row['NM_canonical']
    )

def import_genes():
    # gene_instance = Gene.objects.get(id=1)  # Get the Gene instance
    # CVariant.objects.filter().update(gene=gene_instance)
    # Gene.objects.filter(id__gt=1).delete()
    SEQUENCING_FILES_SOURCE_DIRECTORY = os.path.join(settings.SMB_DIRECTORY_SEQUENCINGDATA, "ProcessedData")
    p = Path("/Users/cbagci/Downloads/MANE.GRCh38.csv")
    # file = os.path.join(SEQUENCING_FILES_SOURCE_DIRECTORY, "cns_files.csv")
    file = Path(Path(__file__).parent.parent / "uploads" / "MANE_hg19_final_filtered.csv")
    df = pd.read_csv(p, index_col=False)
    df = df.reset_index()
    df.apply(create_genes, axis=1)
    pass


if __name__ == "__main__":
    print("start")
    import_genes()
    print("end")
