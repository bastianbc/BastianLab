import os
import boto3
import traceback
import logging
from concurrent.futures import ThreadPoolExecutor
from django.conf import settings
from django.core.cache import cache
from analysisrun.models import AnalysisRun, VariantFile
from analysisrun.handlers import AlignmentsFolderHandler, CnvFolderHandler, SnvFolderHandler

logger = logging.getLogger("file")

class VariantImporter:
    """
    Variant file importer with progress and error tracking (synchronous version).
    """

    def __init__(self, ar_name: str):
        self.ar_name = ar_name
        self.analysis_run = AnalysisRun.objects.get(name=ar_name)
        self.folder_path = f"sequencingdata/ProcessedData/{self.analysis_run.sheet_name}"

        self.folder_types = {
            # "metrics": {"path": "alignments/metrics", "endfix": [".dup_metrics"], "handler": AlignmentsFolderHandler},
            # "cnv": {"path": "cnv/output", "endfix": [".cns", ".diagram.pdf", ".scatter.png"],"handler": CnvFolderHandler},
            "snv": {"path": "snv/output", "endfix": ["_multianno_Filtered.txt"], "handler": SnvFolderHandler},
        }

        self.all_files = []
        self.processed_files = 0
        self.total_files = 0
        self.s3 = boto3.client("s3", region_name=settings.AWS_S3_REGION_NAME)

    # ----------------------------------------------------------------------
    # File Discovery
    # ----------------------------------------------------------------------
    def discover_files_s3(self):
        """Scan S3 bucket and find variant files to process."""
        self.all_files.clear()
        paginator = self.s3.get_paginator("list_objects_v2")

        for page in paginator.paginate(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Prefix=self.folder_path):
            for obj in page.get("Contents", []):
                key = obj["Key"]
                file_name = key.split("/")[-1]
                for type_name, ft in self.folder_types.items():
                    if any(file_name.endswith(e) for e in ft["endfix"]):
                        full_s3_path = (
                            f"https://s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/"
                            f"{settings.AWS_STORAGE_BUCKET_NAME}/{key}"
                        )
                        self.all_files.append((type_name, full_s3_path))

        self.total_files = len(self.all_files)
        self.processed_files = 0
        return self.all_files

    # ----------------------------------------------------------------------
    # Cache helpers
    # ----------------------------------------------------------------------
    def _cache_key(self):
        return f"import_status_{self.ar_name}"

    def _set_status(self, status, progress=0, error=None):
        cache.set(
            self._cache_key(),
            {
                "status": status,
                "processed_files": self.processed_files,
                "progress": progress,
                "error": error,
            },
            timeout=60 * 60,  # 1 hour
        )

    def _update_progress(self):
        """Recalculate and update progress in cache."""
        progress = int((self.processed_files / self.total_files) * 100) if self.total_files else 0
        self._set_status("processing", progress)
        return progress

    # ----------------------------------------------------------------------
    # Main Import Logic (synchronous)
    # ----------------------------------------------------------------------
    def start_import(self, force_restart=False):
        """
        Start the import process synchronously.
        If an import is already in progress and force_restart=False,
        this method will not restart it.
        """
        self.processed_files = VariantFile.objects.filter(analysis_run=self.analysis_run).count()
        cache_data = cache.get(self._cache_key(), {})
        current_status = cache_data.get("status")

        if current_status == "processing" and not force_restart:
            return {
                "status": "processing",
                "processed_files": cache_data.get("processed_files", 0),
                "progress": cache_data.get("progress", 0),
            }

        # Initialize status and discover files
        self._set_status("processing", 0)
        self.discover_files_s3()

        # Run import synchronously
        return self._run_import_job()

    # ----------------------------------------------------------------------
    # Internal import runner
    # ----------------------------------------------------------------------
    def _run_import_job(self):
        """Sequentially process discovered files."""
        try:
            print(f"Starting variant import for {self.ar_name} ({self.total_files} files)")
            for idx, (type_name, file_path) in enumerate(self.all_files, start=1):
                try:
                    print(f"Processing file {idx}/{self.total_files}: {file_path}")
                    handler_class = self.folder_types[type_name]["handler"]
                    success, message = handler_class().process(self.analysis_run, file_path)
                    if success:
                        self.processed_files += 1
                    else:
                        self._set_status("error", self._update_progress(), error=message)
                        logger.error(f"Handler failed for {file_path}: {message}")
                        break
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}", exc_info=True)
                    self._set_status("error", self._update_progress(), error=str(e))
                    self.analysis_run.status = "failed"
                    self.analysis_run.save()
                    return {"status": "error", "error": str(e)}

                # Update progress every iteration
                self._update_progress()

            # Mark completion
            self._set_status("done", 100)
            self.analysis_run.status = "completed"
            self.analysis_run.save()
            logger.info(f"Variant import completed for {self.ar_name}")

            return {
                "status": "done",
                "processed_files": self.processed_files,
                "progress": 100,
            }

        except Exception as e:
            logger.critical(f"Fatal error in variant import for {self.ar_name}: {e}", exc_info=True)
            self._set_status("error", self._update_progress(), error=str(e))
            self.analysis_run.status = "failed"
            self.analysis_run.save()
            return {"status": "error", "error": str(e)}

    # ----------------------------------------------------------------------
    # Utilities
    # ----------------------------------------------------------------------
    def get_progress(self):
        """Return current progress, status, and error (if any)."""
        cache_data = cache.get(self._cache_key())
        if not cache_data:
            return {"status": "not_started", "progress": 0, "error": None}

        if cache_data["status"] == "processing":
            cache_data["progress"] = self._update_progress()
            cache.set(self._cache_key(), cache_data, timeout=60 * 60)

        return cache_data

    def reset_status(self):
        """Reset the status of the import."""
        self._set_status("not_started", 0)



#
# class VariantImporter:
#     """
#     Background variant file importer with progress and error tracking.
#     """
#
#     executor = ThreadPoolExecutor(max_workers=2)  # Shared thread pool
#
#     def __init__(self, ar_name: str):
#         self.ar_name = ar_name
#         self.analysis_run = AnalysisRun.objects.get(name=ar_name)
#         self.folder_path = f"sequencingdata/ProcessedData/{self.analysis_run.sheet_name}"  # S3 prefix (no bucket name)
#
#         self.folder_types = {
#             # "metrics": {"path": "alignments/metrics", "endfix": [".dup_metrics"], "handler": AlignmentsFolderHandler},
#             # "cnv": {"path": "cnv/output", "endfix": [".cns", ".diagram.pdf", ".scatter.png"], "handler": CnvFolderHandler},
#             "snv": {"path": "snv/output", "endfix": ["_multianno_Filtered.txt"], "handler": SnvFolderHandler},
#         }
#
#         self.all_files = []
#         self.processed_files = 0
#         self.total_files = 0
#
#         self.s3 = boto3.client("s3", region_name=settings.AWS_S3_REGION_NAME)
#
#
#     def discover_files_s3(self):
#         """Scan S3 bucket and find variant files to process."""
#         self.all_files.clear()
#         paginator = self.s3.get_paginator("list_objects_v2")
#
#         for page in paginator.paginate(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Prefix=self.folder_path):
#             for obj in page.get("Contents", []):
#                 key = obj["Key"]
#                 file_name = key.split("/")[-1]
#                 for type_name, ft in self.folder_types.items():
#                     if any(file_name.endswith(e) for e in ft["endfix"]):
#                         full_s3_path = f"https://s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{settings.AWS_STORAGE_BUCKET_NAME}/{key}"
#                         self.all_files.append((type_name, full_s3_path))
#
#         self.total_files = len(self.all_files)
#         self.processed_files = 0
#         return self.all_files
#
#     def _cache_key(self):
#         return f"import_status_{self.ar_name}"
#
#     def _set_status(self, status, progress=0, error=None):
#         cache.set(
#             self._cache_key(),
#             {"status": status, "processed_files": self.processed_files, "progress": progress, "error": error},
#             timeout=60 * 60,  # 1 hour
#         )
#
#     def _update_progress(self):
#         """Recalculate progress based on VariantFile count."""
#         progress = int((self.processed_files / self.total_files) * 100) if self.total_files else 0
#         self._set_status("processing", progress)
#         return progress
#
#     def start_import(self, force_restart=False):
#         """
#         Start the import process in the background.
#         If an import is running, it will not restart unless force_restart=True.
#         """
#         self.processed_files = VariantFile.objects.filter(analysis_run=self.analysis_run).count()
#         cache_data = cache.get(self._cache_key(), {})
#         current_status = cache_data.get("status")
#
#         # Don't start another job if already running
#         if current_status == "processing" and not force_restart:
#             return {"status": "processing", "processed_files": cache_data.get("processed_files", 0), "progress": cache_data.get("progress", 0)}
#
#         # Reset cache to "processing"
#         self._set_status("processing", 0)
#
#         # Discover files before starting
#         self.discover_files_s3()
#
#         # Submit background job
#         self.executor.submit(self._background_job)
#         return {"status": "processing", "processed_files": self.processed_files, "progress": 0}
#
#     def _background_job(self):
#             """Internal background thread job for import."""
#         # try:
#             print(f"Starting variant import for {self.ar_name} ({self.total_files} files)")
#             for idx, (type_name, file_path) in enumerate(self.all_files, start=1):
#                 # try:
#                     print("&&&& file: ",type_name, file_path)
#                     handler_class = self.folder_types[type_name]["handler"]
#                     success, message = handler_class().process(self.analysis_run, file_path)
#                     if success:
#                         self.processed_files += 1
#                 # except Exception as e:
#                 #     print(f"Error processing file {file_path}: {e}")
#                 #     self._set_status("error", self._update_progress(), error=str(e))
#                 #     return
#
#             # Set status to done when all files are processed successfully
#             print(f"Variant import completed successfully for {self.ar_name}")
#             self._set_status("done", 100)
#
#             self.analysis_run.status = "completed"
#             self.analysis_run.save()
#
#         # except Exception as e:
#         #     print(f"Fatal error in import for {self.ar_name}: {e}")
#         #     self._set_status("error", self._update_progress(), error=str(e))
#         #     self.analysis_run.status = "failed"
#         #     self.analysis_run.save()
#         #     return
#
#     def get_progress(self):
#         """Return current progress, status, and error (if any)."""
#         cache_data = cache.get(self._cache_key(), None)
#         if not cache_data:
#             return {"status": "not_started", "progress": 0, "error": None}
#
#         if cache_data["status"] == "processing":
#             progress = self._update_progress()
#             cache_data["progress"] = progress
#             cache.set(self._cache_key(), cache_data, timeout=60 * 60)
#
#         return cache_data
#
#     def reset_status(self):
#         """Reset the status of the import."""
#         self._set_status("not_started", 0)