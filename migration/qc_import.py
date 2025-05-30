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

def collect_insert_size_histogram():
    for root, dirs, files in os.walk("/Volumes/sequencingdata/ProcessedData/Analysis.tumor-only"):
        for file in files:
            if "insert_size_histogram.pdf" in file.lower():
                print(file, "---path: ",root.replace("/Volumes/sequencingdata/",""))
                create_variant_file(file, root.replace("/Volumes/sequencingdata/",""), "qc")

def get_insert_size_histogram(variant_file):
    return next(
        (
            file for file in os.listdir(os.path.join(settings.SMB_DIRECTORY_SEQUENCINGDATA, variant_file.directory))
            if "insert_size_histogram.pdf" in file), None
    )



def create_qc_sample(metrics, file, type, variant_file):
    '''
    {'unpaired_reads_examined': '1422', 'read_pairs_examined': '6078719', 'secondary_or_supplementary_rds': '191953', 'unmapped_reads': '1752', 'unpaired_read_duplicates': 1211.0, 'read_pair_duplicates': 3884092.0, 'read_pair_optical_duplicates': 17231.0, 'percent_duplication': 0.63899, 'estimated_library_size': 2381452.0}

    '''
    SampleQC.objects.create(
        sample_lib=get_sample_lib(file),
        analysis_run=AnalysisRun.objects.get(name="AR_ALL"),
        sequencing_run=get_sequencing_run(file),
        variant_file=variant_file,
        type=type,
        insert_size_histogram=get_insert_size_histogram(variant_file).replace("/Volumes/sequencingdata/",""),
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
        median_insert_size=int(float(metrics.get('median_insert_size', 0))) if metrics.get(
            'median_insert_size') is not None else None,
        mode_insert_size=int(float(metrics.get('mode_insert_size', 0))) if metrics.get(
            'median_insert_size') is not None else None,
        mean_insert_size=metrics.get('mean_insert_size', None),
    )

def parse_parse_dup_metrics():
    SampleQC.objects.filter().delete()
    variant_files = VariantFile.objects.filter(type='qc', name__icontains='dup_metrics', directory__icontains="hg38_ProcessedData")
    print("="*30, "dup_metrics", "="*30)
    for file in variant_files:
        print(os.path.join(file.directory,file.name))
        path = os.path.join(settings.SMB_DIRECTORY_SEQUENCINGDATA,file.directory,file.name)
        metrics = parse_dup_metrics(path)
        create_qc_sample(metrics, file.directory.split('/')[-1], 'dup', file)

    variant_files = VariantFile.objects.filter(type='qc', name__icontains='hs_metrics', directory__icontains="hg38_ProcessedData")
    print("="*30, "hs_metrics", "="*30)
    for file in variant_files:
        print(os.path.join(file.directory,file.name))
        path = os.path.join(settings.SMB_DIRECTORY_SEQUENCINGDATA,file.directory,file.name)
        metrics = parse_hs_metrics(path)
        create_qc_sample(metrics, file.directory.split('/')[-1], 'hs', file)

    variant_files = VariantFile.objects.filter(type='qc', name__icontains='insert_size_metrics', directory__icontains="hg38_ProcessedData")
    print("="*30, "insert_size_metrics", "="*30)
    for file in variant_files:
        print(os.path.join(file.directory,file.name))
        path = os.path.join(settings.SMB_DIRECTORY_SEQUENCINGDATA,file.directory,file.name)
        metrics = parse_insert_size_metrics(path)
        create_qc_sample(metrics, file.directory.split('/')[-1], "insert_size", file)


def import_qc():
    parse_parse_dup_metrics()



from qc.models import SampleQC
from variant.models import  VariantFile


def merge_sample_qc_metrics():
    """
    Merge multiple SampleQC records (dup, hs, insert_size) for the same sample
    into a single consolidated record, eliminating NULL values.
    """
    merge_query = '''
        SELECT * FROM sample_qc qc where 
            qc.insert_size_histogram       IS NULL
          OR qc.unpaired_reads_examined   IS NULL
          OR qc.read_pairs_examined       IS NULL
          OR qc.secondary_or_supplementary_rds IS NULL
          OR qc.unmapped_reads            IS NULL
          OR qc.unpaired_read_duplicates  IS NULL
          OR qc.read_pair_duplicates      IS NULL
          OR qc.read_pair_optical_duplicates IS NULL
          OR qc.percent_duplication       IS NULL
          OR qc.estimated_library_size    IS NULL
          OR qc.pct_off_bait              IS NULL
          OR qc.mean_bait_coverage        IS NULL
          OR qc.mean_target_coverage      IS NULL
          OR qc.median_target_coverage    IS NULL
          OR qc.pct_target_bases_1x       IS NULL
          OR qc.pct_target_bases_2x       IS NULL
          OR qc.pct_target_bases_10x      IS NULL
          OR qc.pct_target_bases_20x      IS NULL
          OR qc.pct_target_bases_30x      IS NULL
          OR qc.pct_target_bases_40x      IS NULL
          OR qc.pct_target_bases_50x      IS NULL
          OR qc.pct_target_bases_100x     IS NULL
          OR qc.at_dropout                IS NULL
          OR qc.gc_dropout                IS NULL
          OR qc.median_insert_size        IS NULL
          OR qc.mode_insert_size          IS NULL
          OR qc.mean_insert_size          IS NULL
          
        
        WITH merged AS (
          SELECT
            qc.sample_lib_id,
            qc.sequencing_run_id,
            f.directory,
            MAX(qc.insert_size_histogram)           AS insert_size_histogram,
            MAX(qc.unpaired_reads_examined)         AS unpaired_reads_examined,
            MAX(qc.read_pairs_examined)             AS read_pairs_examined,
            MAX(qc.secondary_or_supplementary_rds)  AS secondary_or_supplementary_rds,
            MAX(qc.unmapped_reads)                  AS unmapped_reads,
            MAX(qc.unpaired_read_duplicates)        AS unpaired_read_duplicates,
            MAX(qc.read_pair_duplicates)            AS read_pair_duplicates,
            MAX(qc.read_pair_optical_duplicates)    AS read_pair_optical_duplicates,
            MAX(qc.percent_duplication)             AS percent_duplication,
            MAX(qc.estimated_library_size)          AS estimated_library_size,
            MAX(qc.pct_off_bait)                    AS pct_off_bait,
            MAX(qc.mean_bait_coverage)              AS mean_bait_coverage,
            MAX(qc.mean_target_coverage)            AS mean_target_coverage,
            MAX(qc.median_target_coverage)          AS median_target_coverage,
            MAX(qc.pct_target_bases_1x)             AS pct_target_bases_1x,
            MAX(qc.pct_target_bases_2x)             AS pct_target_bases_2x,
            MAX(qc.pct_target_bases_10x)            AS pct_target_bases_10x,
            MAX(qc.pct_target_bases_20x)            AS pct_target_bases_20x,
            MAX(qc.pct_target_bases_30x)            AS pct_target_bases_30x,
            MAX(qc.pct_target_bases_40x)            AS pct_target_bases_40x,
            MAX(qc.pct_target_bases_50x)            AS pct_target_bases_50x,
            MAX(qc.pct_target_bases_100x)           AS pct_target_bases_100x,
            MAX(qc.at_dropout)                      AS at_dropout,
            MAX(qc.gc_dropout)                      AS gc_dropout,
            MAX(qc.median_insert_size)              AS median_insert_size,
            MAX(qc.mode_insert_size)                AS mode_insert_size,
            MAX(qc.mean_insert_size)                AS mean_insert_size
          FROM sample_qc qc
          JOIN variant_file f
            ON f.id = qc.variant_file_id
          GROUP BY
            qc.sample_lib_id,
            qc.sequencing_run_id,
            f.directory
        )
        UPDATE sample_qc qc
        SET
          insert_size_histogram            = COALESCE(qc.insert_size_histogram, m.insert_size_histogram),
          unpaired_reads_examined          = COALESCE(qc.unpaired_reads_examined, m.unpaired_reads_examined),
          read_pairs_examined              = COALESCE(qc.read_pairs_examined, m.read_pairs_examined),
          secondary_or_supplementary_rds   = COALESCE(qc.secondary_or_supplementary_rds, m.secondary_or_supplementary_rds),
          unmapped_reads                   = COALESCE(qc.unmapped_reads, m.unmapped_reads),
          unpaired_read_duplicates         = COALESCE(qc.unpaired_read_duplicates, m.unpaired_read_duplicates),
          read_pair_duplicates             = COALESCE(qc.read_pair_duplicates, m.read_pair_duplicates),
          read_pair_optical_duplicates     = COALESCE(qc.read_pair_optical_duplicates, m.read_pair_optical_duplicates),
          percent_duplication              = COALESCE(qc.percent_duplication, m.percent_duplication),
          estimated_library_size           = COALESCE(qc.estimated_library_size, m.estimated_library_size),
          pct_off_bait                     = COALESCE(qc.pct_off_bait, m.pct_off_bait),
          mean_bait_coverage               = COALESCE(qc.mean_bait_coverage, m.mean_bait_coverage),
          mean_target_coverage             = COALESCE(qc.mean_target_coverage, m.mean_target_coverage),
          median_target_coverage           = COALESCE(qc.median_target_coverage, m.median_target_coverage),
          pct_target_bases_1x              = COALESCE(qc.pct_target_bases_1x, m.pct_target_bases_1x),
          pct_target_bases_2x              = COALESCE(qc.pct_target_bases_2x, m.pct_target_bases_2x),
          pct_target_bases_10x             = COALESCE(qc.pct_target_bases_10x, m.pct_target_bases_10x),
          pct_target_bases_20x             = COALESCE(qc.pct_target_bases_20x, m.pct_target_bases_20x),
          pct_target_bases_30x             = COALESCE(qc.pct_target_bases_30x, m.pct_target_bases_30x),
          pct_target_bases_40x             = COALESCE(qc.pct_target_bases_40x, m.pct_target_bases_40x),
          pct_target_bases_50x             = COALESCE(qc.pct_target_bases_50x, m.pct_target_bases_50x),
          pct_target_bases_100x            = COALESCE(qc.pct_target_bases_100x, m.pct_target_bases_100x),
          at_dropout                       = COALESCE(qc.at_dropout, m.at_dropout),
          gc_dropout                       = COALESCE(qc.gc_dropout, m.gc_dropout),
          median_insert_size               = COALESCE(qc.median_insert_size, m.median_insert_size),
          mode_insert_size                 = COALESCE(qc.mode_insert_size, m.mode_insert_size),
          mean_insert_size                 = COALESCE(qc.mean_insert_size, m.mean_insert_size)
        FROM merged m, variant_file f
        WHERE
          qc.variant_file_id = f.id
          AND f.directory = m.directory
          AND qc.sample_lib_id = m.sample_lib_id
          AND qc.sequencing_run_id = m.sequencing_run_id
          AND (
            qc.insert_size_histogram       IS NULL
          OR qc.unpaired_reads_examined   IS NULL
          OR qc.read_pairs_examined       IS NULL
          OR qc.secondary_or_supplementary_rds IS NULL
          OR qc.unmapped_reads            IS NULL
          OR qc.unpaired_read_duplicates  IS NULL
          OR qc.read_pair_duplicates      IS NULL
          OR qc.read_pair_optical_duplicates IS NULL
          OR qc.percent_duplication       IS NULL
          OR qc.estimated_library_size    IS NULL
          OR qc.pct_off_bait              IS NULL
          OR qc.mean_bait_coverage        IS NULL
          OR qc.mean_target_coverage      IS NULL
          OR qc.median_target_coverage    IS NULL
          OR qc.pct_target_bases_1x       IS NULL
          OR qc.pct_target_bases_2x       IS NULL
          OR qc.pct_target_bases_10x      IS NULL
          OR qc.pct_target_bases_20x      IS NULL
          OR qc.pct_target_bases_30x      IS NULL
          OR qc.pct_target_bases_40x      IS NULL
          OR qc.pct_target_bases_50x      IS NULL
          OR qc.pct_target_bases_100x     IS NULL
          OR qc.at_dropout                IS NULL
          OR qc.gc_dropout                IS NULL
          OR qc.median_insert_size        IS NULL
          OR qc.mode_insert_size          IS NULL
          OR qc.mean_insert_size          IS NULL
          );
  '''


if __name__ == "__main__":
    print("start")
    results = merge_sample_qc_metrics()
    print(f"Merged {results['merged_count']} sample groups")
    print(f"Skipped {results['skipped_count']} sample groups (no duplicates)")
    print("end")
