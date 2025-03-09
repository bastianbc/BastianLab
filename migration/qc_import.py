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
from qc.helper import parse_dup_metrics, parse_hs_metrics, parse_insert_size_metrics
from qc.models import SampleQC
from analysisrun.models import AnalysisRun

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
            print(seq_run)
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

def get_sample_lib(filename):
    logger.debug(f"Getting sample lib from filename: {filename}")
    name = filename.split(".")[1]
    logger.debug(f"Extracted sample lib name: {name}")
    try:
        sample_lib = SampleLib.objects.get(name=name)
        print(sample_lib)
        logger.info(f"Found sample lib: {sample_lib}")
        return sample_lib
    except Exception as e:
        logger.error(f"Error finding sample lib with name {name}: {str(e)}")
        return None
    logger.warning(f"Could not extract sample lib name from filename: {filename}")
    return None

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
            pass
            # variant_file_parser(os.path.join(file_path,file.name), "AR_ALL")


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

def create_variant_file(file,dir,type):
    VariantFile.objects.get_or_create(
        name=file,
        directory=dir,
        type=type,
    )

def collect_qc():
    for root, dirs, files in os.walk("/Volumes/sequencingdata/ProcessedData/Analysis.tumor-only"):
        for file in files:
            if "metrics" in file.lower():
                print(file, "---path: ",root.replace("/Volumes/sequencingdata/",""))
                create_variant_file(file, root.replace("/Volumes/sequencingdata/",""), "qc")

def create_qc_sample(metrics, file):
    '''
    {'unpaired_reads_examined': '1422', 'read_pairs_examined': '6078719', 'secondary_or_supplementary_rds': '191953', 'unmapped_reads': '1752', 'unpaired_read_duplicates': 1211.0, 'read_pair_duplicates': 3884092.0, 'read_pair_optical_duplicates': 17231.0, 'percent_duplication': 0.63899, 'estimated_library_size': 2381452.0}

    '''
    SampleQC.objects.create(
        sample_lib=get_sample_lib(file),
        analysis_run=AnalysisRun.objects.get(name="AR_ALL"),
        sequencing_run=get_sequencing_run(file),
        unpaired_reads_examined=metrics.get('unpaired_reads_examined', None),
        read_pairs_examined=metrics.get('read_pairs_examined', None),
        secondary_or_supplementary_rds=metrics.get('secondary_or_supplementary_rds', None),
        unmapped_reads=metrics.get('unmapped_reads', None),
        unpaired_read_duplicates=metrics.get('unpaired_read_duplicates', None),
        read_pair_duplicates=metrics.get('read_pair_duplicates', None),
        read_pair_optical_duplicates=metrics.get('read_pair_optical_duplicates', None),
        percent_duplication=metrics.get('percent_duplication', None),
        estimated_library_size=metrics.get('estimated_library_size', None),
        pct_off_bait=metrics.get('pct_off_bait', None),
        mean_bait_coverage=metrics.get('mean_bait_coverage', None),
        mean_target_coverage=metrics.get('mean_target_coverage', None),
        median_target_coverage=metrics.get('median_target_coverage', None),
        pct_target_bases_1x=metrics.get('pct_target_bases_1x', None),
        pct_target_bases_2x=metrics.get('pct_target_bases_2x', None),
        pct_target_bases_10x=metrics.get('pct_target_bases_10x', None),
        pct_target_bases_20x=metrics.get('pct_target_bases_20x', None),
        pct_target_bases_30x=metrics.get('pct_target_bases_30x', None),
        pct_target_bases_40x=metrics.get('pct_target_bases_40x', None),
        pct_target_bases_50x=metrics.get('pct_target_bases_50x', None),
        pct_target_bases_100x=metrics.get('pct_target_bases_100x', None),
        at_dropout=metrics.get('at_dropout', None),
        gc_dropout=metrics.get('gc_dropout', None),
        median_insert_size=metrics.get('median_insert_size', None),
        mode_insert_size=metrics.get('mode_insert_size', None),
        mean_insert_size=metrics.get('mean_insert_size', None),
    )

def parse_parse_dup_metrics():
    # dup_metrics = VariantFile.objects.filter(type='qc', name__icontains='dup_metrics')
    # for file in dup_metrics:
    #     path = os.path.join(settings.SMB_DIRECTORY_SEQUENCINGDATA,file.directory,file.name)
    #     metrics = parse_dup_metrics(path)
    #     create_qc_sample(metrics, file.directory.split('/')[-1])

    # dup_metrics = VariantFile.objects.filter(type='qc', name__icontains='hs_metrics')
    # for file in dup_metrics:
    #     path = os.path.join(settings.SMB_DIRECTORY_SEQUENCINGDATA,file.directory,file.name)
    #     metrics = parse_hs_metrics(path)
    #     create_qc_sample(metrics, file.directory.split('/')[-1])
        # create_qc_sample(metrics, file.directory.split('/')[-1])

        # print(path, metrics)

    dup_metrics = VariantFile.objects.filter(type='qc', name__icontains='insert_size_metrics')
    for file in dup_metrics:
        path = os.path.join(settings.SMB_DIRECTORY_SEQUENCINGDATA,file.directory,file.name)
        metrics = parse_insert_size_metrics(path)
        # print(path, metrics)
        create_qc_sample(metrics, file.directory.split('/')[-1])


def import_qc():

    SEQUENCING_FILES_SOURCE_DIRECTORY = os.path.join(settings.SMB_DIRECTORY_SEQUENCINGDATA, "ProcessedData")
    parse_parse_dup_metrics()

    pass


if __name__ == "__main__":
    print("start")
    import_qc()
    print("end")
