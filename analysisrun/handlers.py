import os
from analysisrun.models import AnalysisRun, VariantFile
from cns.models import Cns
from cns.helper import parse_cns_file_with_handler
import pandas as pd
from qc.helper import parse_dup_metrics_with_handler
from variant.helper import variant_file_parser, variant_file_parser_with_handler

class AlignmentsFolderHandler:
    def __init__(self):
        pass

    def process(self, analysis_run, file_path):
        print(f"Processing alignments file: {file_path}")

        variant_file, _ = VariantFile.objects.get_or_create(
            name=file_path.split('/')[-1], 
            directory=os.path.dirname(file_path), 
            analysis_run=analysis_run, 
            type="variant", 
            defaults={
                "status": "processing"
            }
        )

        success, message = parse_dup_metrics_with_handler(analysis_run, file_path)
        status = "completed" if success else "failed"
        variant_file.status = status
        variant_file.save()
        
        return success, message

class CnvFolderHandler:
    def __init__(self):
        pass

    def process(self, analysis_run, file_path):
        print(f"Processing cnv file: {file_path}")

        variant_file, _ = VariantFile.objects.get_or_create(
            name=file_path.split('/')[-1], 
            directory=os.path.dirname(file_path), 
            analysis_run=analysis_run, 
            type="variant", 
            defaults={
                "status": "processing"
            }
        )
        
        success, message = parse_cns_file_with_handler(analysis_run, file_path)                
        status = "completed" if success else "failed"
        variant_file.status = status
        variant_file.save()

        return success, message

class SnvFolderHandler:
    def __init__(self):
        pass

    def process(self, analysis_run, file_path):
        print(f"Processing snv file: {file_path}")
        
        variant_file, _ = VariantFile.objects.get_or_create(
            name=file_path.split('/')[-1], 
            directory=os.path.dirname(file_path), 
            analysis_run=analysis_run, 
            type="variant", 
            defaults={
                "status": "processing"
            }
        )
        
        success, message = variant_file_parser_with_handler(analysis_run=analysis_run, variant_file=variant_file)
        print("success: {0}, message: {1}".format(success, message))
        status = "completed" if success else "failed"
        variant_file.status = status
        variant_file.save()
        
        return success, message
