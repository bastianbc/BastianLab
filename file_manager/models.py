import os.path
from pathlib import Path
from django.conf import settings
from django.db import models
from django.db.models import Q
import json
from concurrent.futures import ThreadPoolExecutor


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

    def list_files(self, sub_dir="", exact_dir=None, **kwargs):
        """List all files in the SMB directory."""
        directory = self._resolve_directory(sub_dir, exact_dir)
        return [
            {"id":1, "name": entry.name, "dir": entry.path, "type": "file", "size": None}
            for entry in os.scandir(directory) if entry.is_file()
        ]

    def list_directories(self, sub_dir="", exact_dir=None, **kwargs):
        """List all directories in the SMB directory."""
        directory = self._resolve_directory(sub_dir, exact_dir)
        return [
            {"id":1, "name": entry.name, "dir": entry.path, "type": "directory", "size": None}
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
            draw = kwargs.get('draw', None)[0]
            print("draw: "*10,
                kwargs.get('sub_dir', None),
                kwargs.get('exact_dir', None),
                kwargs.get('draw', None),
                kwargs.get('start', None),
                kwargs.get('length', None),
            )
            draw = int(kwargs.get('draw', [0])[0])
            start = int(kwargs.get('start', [0])[0])
            length = int(kwargs.get('length', [10])[0])
            print("1"*10)
            queryset = _get_authorizated_queryset(**kwargs)
            total = len(queryset)
            print("total"*10, total)
            paginated_items = queryset[start:start + length]
            print("3"*10)

            print("4"*10)
            count = len(paginated_items)
            print("count"*10, count)
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
