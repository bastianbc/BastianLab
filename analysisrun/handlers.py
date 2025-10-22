import os
from analysisrun.models import AnalysisRun, VariantFile
from cns.models import Cns
from cns.helper import parse_cns_file_with_handler
import pandas as pd
from qc.helper import find_sample_libraries_for_analysis_run, parse_dup_metrics
from variant.helper import variant_file_parser

class AlignmentsFolderHandler:
    def __init__(self, folder_path):
        self.folder_path = folder_path

    def process(self):
        print(f"Processing alignments file: {self.folder_path}")
        # Implement specific logic for alignments folder files
        for file in os.listdir(self.folder_path):
            if file.endswith(".dup_metrics"):
                file_path = os.path.join(self.folder_path, file)
                dup_metrics = parse_dup_metrics(file_path)
                sample_qc_files = find_sample_libraries_for_analysis_run(self.analysis_run)
                for sample_qc_file in sample_qc_files:
                    sample_qc_file.dup_metrics_file = file_path
                    sample_qc_file.save()
        return True, "Processed alignments file", {}

class CnvFolderHandler:
    def __init__(self):
        pass

    def process(self, analysis_run, file_path):
        print(f"Processing cnv file: {file_path}")
        parse_cns_file_with_handler(analysis_run, file_path)                
        return True, "Processed cnv file", {}

class SnvFolderHandler:
    def __init__(self):
        pass

    def process(self, analysis_run, file_path):
        print(f"Processing snv file: {file_path}")
        variant_file_parser(file_path, analysis_run)
        return True, "Processed snv file", {}
