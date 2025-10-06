import os.path
import re
from pathlib import Path
from django.conf import settings
from django.db import models
from concurrent.futures import ThreadPoolExecutor
from variant.models import VariantFile
from qc.models import SampleQC
from variant.models import VariantCall
from cns.models import Cns
from django.db.models import Max, Count
from analysisrun.models import AnalysisRun
from sequencingfile.models import SequencingFileSet
from sequencingrun.models import SequencingRun

class FileModel(models.Model):
    """Base model (concrete) to allow proxy models"""
    dummy_field = models.CharField(max_length=1, default="X")  # Dummy field to make it concrete

    class Meta:
        verbose_name = "File Model"
        verbose_name_plural = "File Models"


class FileProxyManager(models.Manager):
    """Custom manager for handling SMB files."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # Ensure proper manager initialization
        self.smb_directory_labshare = settings.BASTIANRAID_DIRECTORY# Corrected attribute name
        self.smb_directory_sequencingdata = settings.SMB_DIRECTORY_SEQUENCINGDATA  # Corrected capitalization
        self.variant_file_locations = ['alignment', 'snv', 'cnv']
        self.VALID_FILENAME_REGEX = re.compile(
            r'^[A-Za-z0-9\-]+(?:_[A-Za-z0-9]+)*\.(?:[A-Z0-9]+_Final\.annovar\.hg19_multianno_Filtered\.txt|Tumor_dedup_BSQR\.cns|fastq\.gz)$'
        )
    def get_variant_file(self, entry, type_, entry_name):
        try:
            if type_ == "directory":
                sr = SequencingRun.objects.filter(name=entry_name)
                print(sr)
                if sr:
                    return sr.first().name
                return "Sequencing Run Not Located"
            else:
                variant = VariantFile.objects.get(name=entry.name.strip())
                return variant.name
        except VariantFile.DoesNotExist:
            return ""

    def get_status(self, type_, source, model, label="QC sample"):
        try:
            if type_ == "file" and not self.VALID_FILENAME_REGEX.match(source):
                return "Does not Apply"


            if label == "Sequencing File Set":
                qs = model.objects.filter(sequencing_files__name=source)
            else:
                parts = source.split(".")
                if len(parts) < 2:
                    return f"Invalid format for {label}"
                sequencing_run, sample_lib = parts[0], parts[1]
                qs = model.objects.filter(sample_lib__name=sample_lib, sequencing_run__name=sequencing_run)

            if type_ == "directory":
                if label == "Sequencing File Set":
                    qs = model.objects.filter(sequencing_run__name=source.split("/")[-1])
                return "Completed" if qs.exists() else "Not Processed"

            status_checks = {
                "SNV Variant": "_filtered.txt",
                "CNS Variant": "bsqr.cns",
                "QC sample": "metrics",
                "Sequencing File Set": "fastq.gz"
            }

            keyword = status_checks.get(label, "")

            if qs.exists():
                return "Completed" if keyword.lower() in source.lower() else "Does not Apply"
            else:
                return "Not Processed"

        except Exception as e:
            return f"{str(e)}"

    def _generate_entry(self, entry, directory, is_file=True):
        type_ = "file" if is_file else "directory"
        entry_name = entry.name
        entry_path = entry.path

        label_model_map = {
            "metrics": (SampleQC, "QC sample"),
            "snv": (VariantCall, "SNV Variant"),
            "cnv": (Cns, "CNS Variant"),
            "HiSeqData": (SequencingFileSet, "Sequencing File Set")
        }

        for key in label_model_map:
            if key in directory:
                model, label = label_model_map[key]
                return {
                    "id": 1,
                    "name": entry_name,
                    "variant_file": self.get_variant_file(entry, type_, entry_name),
                    "dir": entry_path,
                    "type": type_,
                    "status": self.get_status(type_, entry_name, model, label)
                }

        # Default fallback
        return {
            "id": 1,
            "name": entry_name,
            "variant_file": "" if is_file else "",
            "dir": entry_path,
            "type": type_,
            "status": "Does not Apply"
        }

    def list_files(self, sub_dir="", exact_dir=None, **kwargs):
        directory = self._resolve_directory(sub_dir, exact_dir)
        return [
            self._generate_entry(entry, directory, is_file=True)
            for entry in os.scandir(directory) if entry.is_file()
        ]

    def list_directories(self, sub_dir="", exact_dir=None, **kwargs):
        directory = self._resolve_directory(sub_dir, exact_dir)
        return [
            self._generate_entry(entry, directory, is_file=False)
            for entry in os.scandir(directory) if entry.is_dir()
        ]


    def _resolve_directory(self, sub_dir, exact_dir):
        """Resolve the path for the given sub_dir or exact_dir"""
        if exact_dir:
            exact_path = Path(exact_dir[0])
            if not exact_path.is_absolute():
                exact_path = Path("/") / exact_path
            return str(exact_path.resolve())
        elif 'labshare' in sub_dir:
            return self.smb_directory_labshare
        elif 'sequencingdata' in sub_dir:
            return self.smb_directory_sequencingdata
        return "."  # fallback

    def query_by_args(self, **kwargs):
        def _get_authorizated_queryset(**kwargs):
            with ThreadPoolExecutor() as executor:
                future_dirs = executor.submit(self.list_directories, **kwargs)
                future_files = executor.submit(self.list_files, **kwargs)
                return future_dirs.result() + future_files.result()
        try:
            print("_SERVER_SIDE_"*10)
            length_raw = kwargs.get('length', [10])[0]
            length = -1 if length_raw == 'All' else int(length_raw)

            draw = int(kwargs.get('draw', [0])[0])
            start = int(kwargs.get('start', [0])[0])
            queryset = _get_authorizated_queryset(**kwargs)
            total = len(queryset)
            paginated_items = queryset[start:start + length]
            count = len(paginated_items)
            return {
                'items': paginated_items,
                'count': count,
                'total': total,
                'draw': draw
            }
        except Exception as e:
            print(str(e))
            raise

class FileManager(FileModel):
    """Proxy model for managing SMB files."""
    objects = FileProxyManager()

    class Meta:
        proxy = True  # Ensure no database table is created
        verbose_name = "File Manager"
