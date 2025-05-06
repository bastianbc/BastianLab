import os
import re
import logging
import pandas as pd
import django
from pathlib import Path

# Django setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test1.settings")
django.setup()

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from sequencingrun.models import SequencingRun
from variant.models import VariantCall, GVariant, CVariant, PVariant, VariantFile
from analysisrun.models import AnalysisRun
from samplelib.models import SampleLib
from gene.models import Gene

# --- Logger Setup ---
class LoggerSetup:
    @staticmethod
    def get_logger(name="variant_parser"):
        logger = logging.getLogger(name)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.DEBUG)
        return logger

logger = LoggerSetup.get_logger()

# --- File Validation ---
class FileValidator:
    def __init__(self, filepath):
        self.filepath = filepath

    def validate(self):
        if not os.path.exists(self.filepath):
            return False, f"File not found: {self.filepath}"
        if not self.filepath.endswith('.txt'):
            return False, "Invalid file format. Expected .txt file"
        return True, ""

# --- Metadata Extraction ---
class MetadataExtractor:
    @staticmethod
    def extract_caller(filename):
        match = re.match(r'.*?(\w+)_Final', filename)
        return match.group(1) if match else None

    @staticmethod
    def extract_sample_lib(filename):
        match = re.match(r'^[^.]+\.(\w+-\d+)', filename)
        if match:
            try:
                return SampleLib.objects.get(name=match.group(1))
            except SampleLib.DoesNotExist:
                return None
        return None

    @staticmethod
    def extract_sequencing_run(filename):
        base = os.path.splitext(filename)[0]
        try:
            return SequencingRun.objects.get(name=base)
        except SequencingRun.DoesNotExist:
            return None

    @staticmethod
    def extract_hg(filename):
        match = re.search(r'\.hg(\d+)_', filename)
        return match.group(1) if match else None

# --- Variant Row Parser ---
class VariantRowParser:
    def __init__(self, row, filename, analysis_run, variant_file, sample_lib):
        self.row = row
        self.filename = filename
        self.analysis_run = analysis_run
        self.variant_file = variant_file
        self.sample_lib = sample_lib
        self.logger = logger

    def parse(self):
        # Check fields
        if not self._has_required_fields():
            raise ValueError("Missing required fields")

        caller = MetadataExtractor.extract_caller(self.filename)
        sequencing_run = MetadataExtractor.extract_sequencing_run(self.filename)
        hg_version = MetadataExtractor.extract_hg(self.filename)

        # Create VariantCall
        vc = VariantCall.objects.create(
            analysis_run=self.analysis_run,
            sample_lib=self.sample_lib,
            sequencing_run=sequencing_run,
            variant_file=self.variant_file,
            coverage=self.row['Depth'],
            log2r=0.0,
            caller=caller,
            ref_read=self.row['Ref_reads'],
            alt_read=self.row['Alt_reads'],
        )
        # Create GVariant
        gv = GVariant.objects.create(
            variant_call=vc,
            hg=hg_version,
            chrom=self.row['Chr'],
            start=self.row['Start'],
            end=self.row['End'],
            ref=self.row['Ref'],
            alt=self.row['Alt'],
            avsnp150=self.row.get('avsnp150', '')
        )
        # Process gene variants
        self._create_gene_variants(gv)
        return True

    def _has_required_fields(self):
        required = ['Chr','Start','End','Ref','Alt','Depth','Ref_reads','Alt_reads','AAChange.refGene']
        return all(f in self.row and pd.notna(self.row[f]) for f in required)

    def _create_gene_variants(self, g_variant):
        from variant_importer_helpers import create_c_and_p_variants
        create_c_and_p_variants(
            g_variant=g_variant,
            aachange=self.row['AAChange.refGene'],
            func=self.row.get('Func.refGene',''),
            gene_detail=self.row.get('GeneDetail.refGene',''),
            filename=self.filename,
            row_gene=self.row.get('Gene.refGene','')
        )

# --- Variant Importer ---
class VariantImporter:
    def __init__(self, filepath, analysis_run_name):
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.analysis_run = AnalysisRun.objects.filter(name=analysis_run_name).first()
        self.variant_file = VariantFile.objects.filter(name=self.filename).first()
        self.logger = logger
        self.stats = {'total':0,'success':0,'fail':0,'errors':[]}

    def run(self):
        valid, msg = FileValidator(self.filepath).validate()
        if not valid:
            return False, msg, self.stats
        df = pd.read_csv(self.filepath, sep='\t')
        self.stats['total'] = len(df)
        for idx, row in df.iterrows():
            try:
                sample_lib = MetadataExtractor.extract_sample_lib(self.filename)
                parser = VariantRowParser(row, self.filename, self.analysis_run, self.variant_file, sample_lib)
                parser.parse()
                self.stats['success'] += 1
            except Exception as e:
                self.stats['fail'] += 1
                self.stats['errors'].append(f"Row {idx+1}: {e}")
                self.logger.error(f"Row {idx+1} failed: {e}")
        return True, 'Parsing complete', self.stats

# --- Main Execution ---
def import_variants():
    VariantFile.objects.update(call=False)
    for vf in VariantFile.objects.all():
        path = os.path.join(settings.SMB_DIRECTORY_SEQUENCINGDATA, vf.directory, vf.name)
        if '_Filtered' in vf.name:
            importer = VariantImporter(path, 'AR_ALL')
            importer.run()

if __name__ == '__main__':
    print('start')
    import_variants()
    print('end')
