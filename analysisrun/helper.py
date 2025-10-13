import os
import traceback
from concurrent.futures import ThreadPoolExecutor
from django.conf import settings
from django.core.cache import cache
from analysisrun.models import AnalysisRun
from variant.models import VariantFile
from analysisrun.handlers import AlignmentsFolderHandler, CnvFolderHandler, SnvFolderHandler


class VariantImporter:
    """
    Background variant file importer with progress and error tracking.
    """

    executor = ThreadPoolExecutor(max_workers=2)  # Shared thread pool

    def __init__(self, ar_name: str):
        self.ar_name = ar_name
        self.analysis_run = AnalysisRun.objects.get(name=ar_name)
        self.folder_path = os.path.join(settings.VARIANT_FILES_SOURCE_DIRECTORY, ar_name)

        self.folder_types = {
            "metrics": {"path": "alignments/metrics", "endfix": [".dup_metrics"], "handler": AlignmentsFolderHandler},
            "cnv": {"path": "cnv/output", "endfix": [".cns", ".diagram.pdf", ".scatter.png"], "handler": CnvFolderHandler},
            "snv": {"path": "snv/output", "endfix": [".multianno.Filtered.txt"], "handler": SnvFolderHandler},
        }

        self.all_files = []
        self.total_files = 0

    def discover_files(self):
        """Scan the folder and find variant files to process."""
        self.all_files.clear()
        for root, _, files in os.walk(self.folder_path):
            for f in files:
                for type_name, ft in self.folder_types.items():
                    if any(f.endswith(e) for e in ft["endfix"]):
                        full_path = os.path.join(root, f)
                        self.all_files.append((type_name, full_path))
        self.total_files = len(self.all_files)
        return self.all_files

    def _cache_key(self):
        return f"import_status_{self.ar_name}"

    def _set_status(self, status, progress=0, error=None):
        cache.set(
            self._cache_key(),
            {"status": status, "progress": progress, "error": error},
            timeout=60 * 60,  # 1 hour
        )

    def _update_progress(self):
        """Recalculate progress based on VariantFile count."""
        processed_files = VariantFile.objects.filter(analysis_run=self.analysis_run).count()
        progress = round((processed_files / self.total_files) * 100, 2) if self.total_files else 0
        cache_data = cache.get(self._cache_key(), {})
        cache_data.update({"progress": progress})
        cache.set(self._cache_key(), cache_data, timeout=60 * 60)
        return progress

    def start_import(self, force_restart=False):
        """
        Start the import process in the background.
        If an import is running, it will not restart unless force_restart=True.
        """
        cache_data = cache.get(self._cache_key(), {})
        current_status = cache_data.get("status")

        # Don't start another job if already running
        if current_status == "processing" and not force_restart:
            return {"status": "processing", "progress": cache_data.get("progress", 0)}

        # Reset cache to "processing"
        self._set_status("processing", 0)

        # Discover files before starting
        self.discover_files()

        # Submit background job
        self.executor.submit(self._background_job)
        return {"status": "started", "progress": 0, "total_files": self.total_files}

    def _background_job(self):
        """Internal background thread job for import."""
        try:
            print(f"Starting variant import for {self.ar_name} ({self.total_files} files)")
            for idx, (type_name, file_path) in enumerate(self.all_files, start=1):
                try:
                    handler_class = self.folder_types[type_name]["handler"]
                    handler_class(self.ar_name).process(file_path)
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")
                    # Continue processing remaining files
                finally:
                    # Update progress after each file
                    self._update_progress()

            # Finished successfully
            self._set_status("completed", 100)
            print(f"Import completed for {self.ar_name}")

        except Exception as e:
            tb = traceback.format_exc()
            print(f"Fatal error in import for {self.ar_name}: {e}")
            self._set_status("error", self._update_progress(), error=tb)

    def get_progress(self):
        """Return current progress, status, and error (if any)."""
        cache_data = cache.get(self._cache_key(), None)
        if not cache_data:
            return {"status": "not_started", "progress": 0, "error": None}

        if cache_data["status"] == "processing":
            progress = self._update_progress()
            cache_data["progress"] = progress
            cache.set(self._cache_key(), cache_data, timeout=60 * 60)

        return cache_data
