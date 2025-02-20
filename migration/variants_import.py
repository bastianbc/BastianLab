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

    # Handle range variants
    match5 = re.match(r'p\.([A-Z])(\d+)_([A-Z])(\d+)(delins|del|ins)', p_var)
    if match5:
        start, end, reference_residues, inserted_residues, change_type = (
            match5.group(2),
            match5.group(4),
            match5.group(1) + match5.group(3),
            "",
            match5.group(5)
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

    # Handle more complex variants
    match4 = re.match(r'p\.([A-Z]+)(\d+)_([A-Z]+)(\d+)(delins|del|ins)([A-Z]+)', p_var)
    if match4:
        start, end, reference_residues, inserted_residues, change_type = (
            match4.group(2),
            match4.group(4),
            match4.group(1) + match4.group(3),
            match4.group(6),
            match4.group(5)
        )
        logger.debug(f"Parsed p_var successfully: {start, end, reference_residues, inserted_residues, change_type}")
        return start, end, reference_residues, inserted_residues, change_type

    logger.warning(f"Failed to parse p_var: {p_var}")
    print(f"Failed to parse p_var: {p_var}")
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
    match = re.match(r'^[^.]+\.(\w+-\d+)', filename)
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
        print("variant_file: ", variant_file.name)
        logger.info(f"Found variant file: {variant_file}")
        return variant_file
    except ObjectDoesNotExist:
        logger.error(f"Variant file not found: {file_path}")
        return None

def get_gene(name, hg, canonical):
    logger.debug(f"Getting gene: {name}")
    try:
        if "NOTCH2NL" in name or "MUC1" in name or "MUC2" in name:
            gene = Gene.objects.get(name__icontains=name, hg=hg, nm_canonical=canonical)
            return gene
        gene = Gene.objects.get(name=name, hg=hg)
        logger.info(f"Found gene: {name}")
        return gene
    except ObjectDoesNotExist:
        logger.error(f"Gene not found: {name}")
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
    print("$$$", gene_detail, row_gene)
    entries = gene_detail.split(';')
    for entry in entries:
        try:
            logger.debug(f"Processing gene_detail: {entry}")
            nm_id, exon, c_var = entry.split(':')
            gene = get_gene(row_gene, "hg19", nm_id)
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
                    gene_detail=entry,
                    is_alias=is_alias,
                )
                logger.info(f"Created CVariant: {c_variant}")
        except Exception as e:
            logger.error(f"Error processing gene_detail entry '{entry}': {str(e)}")


def create_c_and_p_variants(g_variant, aachange, func, gene_detail, filename, row_gene):
    logger.debug(f"Creating C and P variants for aachange: {aachange}")
    print("aachange: ", aachange, " gene_detail: ", gene_detail)
    entries = aachange.split(',')
    if any(aachange in invalid for invalid in ["UNKNOWN", "."]):
        create_gene_detail(gene_detail, row_gene, g_variant, func)
    else:
        for entry in entries:
            try:
                logger.debug(f"Processing entry: {entry}")
                gene, nm_id, exon, c_var, p_var = entry.split(':')
                gene = get_gene(gene, "hg19", nm_id)
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
                        gene_detail=entry
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


                logger.debug(f"Creating VariantCall for row {index + 1}")
                variant_call = VariantCall.objects.create(
                    analysis_run=analysis_run,
                    sample_lib=sample_lib,
                    sequencing_run=get_sequencing_run(filename),
                    variant_file=variant_file,
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
                    ref=row['Ref'][:99],
                    alt=row['Alt'][:99],
                    avsnp150=row.get('avsnp150', '')
                )

                logger.debug(f"Creating C and P variants for row {index + 1}")
                create_c_and_p_variants(
                    g_variant=g_variant,
                    aachange=row['AAChange.refGene'],
                    func=row['Func.refGene'],
                    gene_detail=row.get('GeneDetail.refGene', ''),
                    filename = filename,
                    row_gene=row['Gene.refGene']
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
    VariantFile.objects.filter().update(call=False)
    files = VariantFile.objects.filter()
    VariantCall.objects.filter().delete()
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
        hg = row['hg'],
        nm_canonical = row['NM_canonical']
    )
    print("Gene: ", gene.name)

def import_genes():
    # gene_instance = Gene.objects.get(id=1)  # Get the Gene instance
    # CVariant.objects.filter().update(gene=gene_instance)
    # Gene.objects.filter(id__gt=1).delete()
    SEQUENCING_FILES_SOURCE_DIRECTORY = os.path.join(settings.SMB_DIRECTORY_SEQUENCINGDATA, "ProcessedData")
    # file = os.path.join(SEQUENCING_FILES_SOURCE_DIRECTORY, "cns_files.csv")
    file = Path(Path(__file__).parent.parent / "uploads" / "MANE_hg19_final_filtered.csv")
    df = pd.read_csv(file, index_col=False)
    df = df.reset_index()
    # df.apply(create_genes, axis=1)
    pass


if __name__ == "__main__":
    print("start")
    import_variants()
    print("end")
