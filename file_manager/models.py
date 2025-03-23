import os.path
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
        self.smb_directory_labshare = settings.SMB_DIRECTORY_LABSHARE# Corrected attribute name
        self.smb_directory_sequencingdata = settings.SMB_DIRECTORY_SEQUENCINGDATA  # Corrected capitalization
        self.variant_file_locations = ['alignment', 'snv', 'cnv']

    def get_variant_file(self, entry):
        try:
            print(VariantFile.objects.get(name=entry.name.strip()))
            return VariantFile.objects.get(name=entry.name.strip()).name
        except:
            # print("Object not found")
            return ""

    def get_status(self, type, source, model, label="QC sample"):
        try:
            parts = source.split(".")
            if len(parts) < 2:
                return f"Invalid format for {label}"
            sequencing_run, sample_lib = parts[0], parts[1]
            if label == "SNV Variant" and type == "file":
                if model.objects.filter(sample_lib__name=sample_lib, sequencing_run__name=sequencing_run).exists() and "_filtered.txt" in source.lower():
                    return "Completed"
                if model.objects.filter(sample_lib__name=sample_lib, sequencing_run__name=sequencing_run).exists() and "_filtered.txt" not in source.lower():
                    return "Does not Apply"
                else:
                    return "Not Processed"
            if label == "CNS Variant" and type == "file":
                if model.objects.filter(sample_lib__name=sample_lib, sequencing_run__name=sequencing_run).exists() and "bsqr.cns" in source.lower():
                    return "Completed"
                if model.objects.filter(sample_lib__name=sample_lib, sequencing_run__name=sequencing_run).exists() and "bsqr.cns" not in source.lower():
                    return "Does not Apply"
                else:
                    return "Not Processed"
            if type == "directory":
                if model.objects.filter(sample_lib__name=sample_lib, sequencing_run__name=sequencing_run).exists():
                    return "Completed"
                else:
                    return "Not Processed"
        except Exception as e:
            return f"{str(e)}"


    def list_files(self, sub_dir="", exact_dir=None, **kwargs):
        """List all files in the SMB directory."""
        directory = self._resolve_directory(sub_dir, exact_dir)
        if not any(variant in directory for variant in self.variant_file_locations):
            return [
                {"id":1, "name": entry.name, "variant_file": "", "dir": entry.path, "type": "file", "status": "Does not Apply"}
                for entry in os.scandir(directory) if entry.is_file()
            ]
        else:
            if "metrics" in directory:
                return [
                    {"id": 1, "name": entry.name, "variant_file": self.get_variant_file(entry=entry),
                     "dir": entry.path, "type": "file", "status": self.get_status("file", entry.name,SampleQC)}
                    for entry in os.scandir(directory) if entry.is_file()
                ]
            elif "snv" in directory:
                return [
                    {"id": 1, "name": entry.name, "variant_file": self.get_variant_file(entry=entry),
                     "dir": entry.path, "type": "file", "status": self.get_status("file", entry.name,VariantCall,"SNV Variant")}
                    for entry in os.scandir(directory) if entry.is_file()
                ]
            elif "cnv" in directory:
                return [
                    {"id": 1, "name": entry.name, "variant_file": self.get_variant_file(entry=entry),
                     "dir": entry.path, "type": "file", "status": self.get_status("file", entry.name, Cns, "CNS Variant")}
                    for entry in os.scandir(directory) if entry.is_file()
                ]



    def list_directories(self, sub_dir="", exact_dir=None, **kwargs):
        """List all directories in the SMB directory."""
        directory = self._resolve_directory(sub_dir, exact_dir)
        if not any(variant in directory for variant in self.variant_file_locations):
            return [
                {"id":1, "name": entry.name, "dir": entry.path, "variant_file": "", "type": "directory", "status": "Does not Apply"}
                for entry in os.scandir(directory) if entry.is_dir()
            ]
        else:
            if "metrics" in directory:
                return [
                    {"id": 1, "name": entry.name, "variant_file": "",
                     "dir": entry.path, "type": "directory", "status": self.get_status("directory", entry.name,SampleQC)}
                    for entry in os.scandir(directory) if entry.is_dir()
                ]
            elif "snv" in directory:
                return [
                    {"id": 1, "name": entry.name, "variant_file": "",
                     "dir": entry.path, "type": "directory", "status": self.get_status("directory", entry.name,VariantCall,"SNV Variant")}
                    for entry in os.scandir(directory) if entry.is_dir()
                ]
            elif "cnv" in directory:
                return [
                    {"id": 1, "name": entry.name, "variant_file": "",
                     "dir": entry.path, "type": "directory", "status": self.get_status("directory", entry.name, Cns, "CNS Variant")}
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
