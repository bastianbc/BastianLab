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
