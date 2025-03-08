import os
import pandas as pd
import logging
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)

BASE_DIR = "/sequencingdata/ProcessedData/"

QC_FILE_EXTENSIONS = {
    "dup_metrics": ".dup_metrics",
    "hs_metrics": ".Hs_Metrics.txt",
    "insert_metrics": ".insert_size_metrics.txt",
    "histogram_pdf": ".Tumor_insert_size_histogram.pdf"
}

def find_sample_libraries_for_analysis_run(arun_id):
    """
    Find all sample libraries associated with a specific analysis run
    by traversing through the directory structure.
    """
    logger.info(f"Searching for sample libraries and QC files for sequencing run: {arun_id}")

    # List to store sample QC file information
    sample_qc_files = []

    # Walk through all directories starting from the base directory
    for root, _, files in os.walk(BASE_DIR):
        # Filter QC files by extensions
        qc_files_in_dir = [f for f in files if any(f.endswith(ext) for ext in QC_FILE_EXTENSIONS.values())]

        # If we found QC files, process them
        for filename in qc_files_in_dir:
            parts = filename.split('.')
            # Check if filename has enough parts and matches the pattern
            if len(parts) >= 3:
                # In format "BCB002.NMLP-001.Tumor.dup_metrics":
                # parts[0] is sequencing run (BCB002)
                # parts[1] is sample library (NMLP-001)
                sequencing_run_name = parts[0]
                sample_lib_name = parts[1]

                # Determine file type
                file_path = os.path.join(root, filename)
                file_type = None

                for qc_type, extension in QC_FILE_EXTENSIONS.items():
                    if filename.endswith(extension):
                        file_type = qc_type
                        break

                if file_type:
                    sample_qc_files.append({
                        'sequencing_run_name': sequencing_run_name,
                        'sample_lib_name': sample_lib_name,
                        'file_type': file_type,
                        'file_path': file_path,
                    })

                    logger.info(f"Found {file_type} file for sequencing run {sequencing_run_name}, sample {sample_lib_name}: {filename}")

    return sample_qc_files

def parse_dup_metrics(file_path):
    """
    Parse duplicate metrics file and extract required values.
    The table starts at row 7.
    """
    try:
        # Check if file exists
        if not file_path or not os.path.exists(file_path):
            logger.error(f"Duplicate metrics file not found: {file_path}")
            return {}

        # Read the file with pandas
        df = pd.read_csv(file_path, sep='\t', skiprows=6)

        # Check if data is present
        if df.empty or len(df) < 2:
            logger.warning(f"Empty or incomplete data in {file_path}")
            return {}

        # Extract row from index 1 (after skipping 6 rows, this is row 7-8)
        row = df.iloc[1]

        # Extract metrics
        metrics = {
            'unpaired_reads_examined': row.get('UNPAIRED_READS_EXAMINED'),
            'read_pairs_examined': row.get('READ_PAIRS_EXAMINED'),
            'secondary_or_supplementary_rds': row.get('SECONDARY_OR_SUPPLEMENTARY_RDS'),
            'unmapped_reads': row.get('UNMAPPED_READS'),
            'unpaired_read_duplicates': row.get('UNPAIRED_READ_DUPLICATES'),
            'read_pair_duplicates': row.get('READ_PAIR_DUPLICATES'),
            'read_pair_optical_duplicates': row.get('READ_PAIR_OPTICAL_DUPLICATES'),
            'percent_duplication': row.get('PERCENT_DUPLICATION'),
            'estimated_library_size': row.get('ESTIMATED_LIBRARY_SIZE')
        }

        # Log any missing metrics
        missing_metrics = [k for k, v in metrics.items() if v is None]
        if missing_metrics:
            logger.warning(f"Missing metrics in {file_path}: {', '.join(missing_metrics)}")

        return metrics

    except Exception as e:
        logger.error(f"Error parsing duplicate metrics file {file_path}: {str(e)}")
        return {}

def parse_hs_metrics(file_path):
    """
    Parse Hs metrics file and extract required values.
    The table starts at row 7.
    """
    try:
        # Check if file exists
        if not file_path or not os.path.exists(file_path):
            logger.error(f"Hs metrics file not found: {file_path}")
            return {}

        # Read the file with pandas
        df = pd.read_csv(file_path, sep='\t', skiprows=6)

        # Check if data is present
        if df.empty or len(df) < 2:
            logger.warning(f"Empty or incomplete data in {file_path}")
            return {}

        # Extract row from index 1 (after skipping 6 rows, this is row 7-8)
        row = df.iloc[1]

        # Extract metrics
        metrics = {
            'pct_off_bait': row.get('PCT_OFF_BAIT'),
            'mean_bait_coverage': row.get('MEAN_BAIT_COVERAGE'),
            'mean_target_coverage': row.get('MEAN_TARGET_COVERAGE'),
            'median_target_coverage': row.get('MEDIAN_TARGET_COVERAGE'),
            'pct_target_bases_1x': row.get('PCT_TARGET_BASES_1X'),
            'pct_target_bases_2x': row.get('PCT_TARGET_BASES_2X'),
            'pct_target_bases_10x': row.get('PCT_TARGET_BASES_10X'),
            'pct_target_bases_20x': row.get('PCT_TARGET_BASES_20X'),
            'pct_target_bases_30x': row.get('PCT_TARGET_BASES_30X'),
            'pct_target_bases_40x': row.get('PCT_TARGET_BASES_40X'),
            'pct_target_bases_50x': row.get('PCT_TARGET_BASES_50X'),
            'pct_target_bases_100x': row.get('PCT_TARGET_BASES_100X'),
            'at_dropout': row.get('AT_DROPOUT'),
            'gc_dropout': row.get('GC_DROPOUT')
        }

        # Log any missing metrics
        missing_metrics = [k for k, v in metrics.items() if v is None]
        if missing_metrics:
            logger.warning(f"Missing metrics in {file_path}: {', '.join(missing_metrics)}")

        return metrics

    except Exception as e:
        logger.error(f"Error parsing Hs metrics file {file_path}: {str(e)}")
        return {}

def parse_insert_size_metrics(file_path):
    """
    Parse insert size metrics file and extract required values.
    The table starts at row 7.
    """
    try:
        # Check if file exists
        if not file_path or not os.path.exists(file_path):
            logger.error(f"Insert size metrics file not found: {file_path}")
            return {}

        # Read the file with pandas
        df = pd.read_csv(file_path, sep='\t', skiprows=6)

        # Check if data is present
        if df.empty or len(df) < 2:
            logger.warning(f"Empty or incomplete data in {file_path}")
            return {}

        # Extract row from index 1 (after skipping 6 rows, this is row 7-8)
        row = df.iloc[1]

        # Extract metrics
        metrics = {
            'median_insert_size': row.get('MEDIAN_INSERT_SIZE'),
            'mode_insert_size': row.get('MODE_INSERT_SIZE'),
            'mean_insert_size': row.get('MEAN_INSERT_SIZE')
        }

        # Log any missing metrics
        missing_metrics = [k for k, v in metrics.items() if v is None]
        if missing_metrics:
            logger.warning(f"Missing metrics in {file_path}: {', '.join(missing_metrics)}")

        return metrics

    except Exception as e:
        logger.error(f"Error parsing insert size metrics file {file_path}: {str(e)}")
        return {}

def group_qc_files_by_sample(qc_files):
    """
    Group QC files by sample library ID.

    Args:
        qc_files: List of dictionaries with QC file info

    Returns:
        Dictionary mapping sample library IDs to their QC files
    """
    sample_libraries = defaultdict(lambda: {'files': {}})

    for file_info in qc_files:
        sample_lib_name = file_info['sample_lib_name']
        sample_libraries[sample_lib_name]['files'][file_info['file_type']] = file_info['file_path']
        sample_libraries[sample_lib_name]['sequencing_run_name'] = file_info['sequencing_run_name']

    return sample_libraries

def process_analysis_run(arun_id):
    """
    Process all samples associated with an analysis run.
    This is the main business flow that starts with an analysis run ID.
    """
    logger.info(f"Starting to process sequencing run: {arun_id}")

    # Find all sample libraries and their QC files in a single pass
    qc_files = find_sample_libraries_for_analysis_run(arun_id)

    sample_libraries = group_qc_files_by_sample(qc_files)

    # Process each sample library
    logger.info(f"Processing {len(sample_libraries)} sample libraries for analysis run {arun_id}")
    results = []

    for sample_lib_name, details in sample_libraries.items():
        try:
            # Get QC files for this sample
            sample_files = details['files']
            sequencing_run_name = details['files']

            # Parse each metrics file
            dup_metrics = parse_dup_metrics(sample_files['dup_metrics'])
            hs_metrics = parse_hs_metrics(sample_files['hs_metrics'])
            insert_metrics = parse_insert_size_metrics(sample_files['insert_metrics'])

            # Combine all metrics into a tabular row
            combined_metrics = {
                'sequencing_run_name': sequencing_run_name,
                'sample_lib_name': sample_lib_name,
                'histogram_pdf_path': sample_files.get('histogram_pdf'),
                **dup_metrics,
                **hs_metrics,
                **insert_metrics
            }

            # Add to results
            results.append(combined_metrics)
            logger.info(f"Successfully processed {sample_lib_name} for analysis run {arun_id}")

        except Exception as e:
            logger.error(f"Error processing {sample_lib_name} for analysis run {arun_id}: {str(e)}")

    return {
        'analysis_run': arun_id,
        'status': summary_status,
        'data': results,
        'summary_report': {}
    }
