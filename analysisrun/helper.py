# import os
# import boto3
# import traceback
# import logging
# from concurrent.futures import ThreadPoolExecutor
# from django.conf import settings
# from django.core.cache import cache
# from analysisrun.models import AnalysisRun, VariantFile
# from analysisrun.handlers import (
#     AlignmentsFolderHandler,
#     CnvFolderHandler,
#     SnvFolderHandler,
#     CnvAttachmentHandler,
# )
#
# logger = logging.getLogger("file")
#
# # ✅ Shared thread pool — reused across all imports
# executor = ThreadPoolExecutor(max_workers=2)
#
#
# class VariantImporter:
#     """
#     Variant file importer with progress and error tracking.
#     Uses ThreadPoolExecutor to run imports asynchronously
#     to prevent Gunicorn or Nginx timeouts.
#     """
#
#     def __init__(self, ar_name: str):
#         self.ar_name = ar_name
#         self.analysis_run = AnalysisRun.objects.get(name=ar_name)
#         self.folder_path = f"sequencingdata/ProcessedData/{self.analysis_run.sheet_name}"
#
#         self.folder_types = {
#             "metrics": {
#                 "path": "alignments/metrics",
#                 "endfix": [
#                     ".dup_metrics",
#                     "_Hs_Metrics.txt",
#                     ".insert_size_metrics.txt",
#                     "insert_size_histogram.pdf",
#                 ],
#                 "handler": AlignmentsFolderHandler,
#             },
#             "cnv": {
#                 "path": "cnv/output",
#                 "endfix": [".cns"],
#                 "handler": CnvFolderHandler,
#             },
#             "cnv_attachments": {
#                 "path": "cnv/output",
#                 "endfix": ["diagram.pdf", "scatter.png"],
#                 "handler": CnvAttachmentHandler,
#             },
#             "snv": {
#                 "path": "snv/output",
#                 "endfix": ["_multianno_Filtered.txt"],
#                 "handler": SnvFolderHandler,
#             },
#         }
#
#         self.all_files = []
#         self.processed_files = 0
#         self.total_files = 0
#         self.s3 = boto3.client("s3", region_name=settings.AWS_S3_REGION_NAME)
#
#     # ----------------------------------------------------------------------
#     # Cache helpers
#     # ----------------------------------------------------------------------
#     def _cache_key(self):
#         return f"import_status_{self.ar_name}"
#
#     def _set_status(self, status, progress=0, error=None):
#         cache.set(
#             self._cache_key(),
#             {
#                 "status": status,
#                 "processed_files": self.processed_files,
#                 "progress": progress,
#                 "total_files": self.total_files,
#                 "error": error,
#             },
#             timeout=60 * 60,  # 1 hour
#         )
#
#     def _update_progress(self):
#         """Recalculate and update progress in cache."""
#         progress = int(
#             (self.processed_files / self.total_files) * 100
#         ) if self.total_files else 0
#         self._set_status("processing", progress)
#         return progress
#
#     # ----------------------------------------------------------------------
#     # File discovery
#     # ----------------------------------------------------------------------
#     def discover_files_s3(self):
#         """Discover files in S3 based on known suffixes."""
#         self.all_files.clear()
#         paginator = self.s3.get_paginator("list_objects_v2")
#         discovered_files = []
#
#         for page in paginator.paginate(
#             Bucket=settings.AWS_STORAGE_BUCKET_NAME, Prefix=self.folder_path
#         ):
#             for obj in page.get("Contents", []):
#                 key = obj["Key"]
#                 file_name = key.split("/")[-1]
#                 for type_name, ft in self.folder_types.items():
#                     if any(file_name.endswith(e) for e in ft["endfix"]):
#                         full_s3_path = (
#                             f"https://s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/"
#                             f"{settings.AWS_STORAGE_BUCKET_NAME}/{key}"
#                         )
#                         discovered_files.append((type_name, full_s3_path))
#
#         priority_order = [
#             "_multianno_Filtered.txt",
#             ".dup_metrics",
#             ".cns",
#             ".diagram.pdf",
#             ".scatter.png",
#         ]
#
#         def sort_key(item):
#             _, path = item
#             name = path.lower()
#             for idx, suffix in enumerate(priority_order):
#                 if name.endswith(suffix.lower()):
#                     return (idx, name)
#             return (len(priority_order), name)
#
#         self.all_files = sorted(discovered_files, key=sort_key)
#         self.total_files = len(self.all_files)
#         self.processed_files = 0
#         self._set_status("processing", 0)
#         return self.all_files
#
#     # ----------------------------------------------------------------------
#     # Main entry point (ASYNC version)
#     # ----------------------------------------------------------------------
#     def start_import(self, force_restart=False):
#         """
#         Starts the import asynchronously using a shared thread pool.
#         Returns immediately — background job continues running.
#         """
#         self.processed_files = VariantFile.objects.filter(
#             analysis_run=self.analysis_run
#         ).count()
#         cache_data = cache.get(self._cache_key(), {})
#         current_status = cache_data.get("status")
#
#         if current_status == "processing" and not force_restart:
#             return {
#                 "status": "processing",
#                 "processed_files": cache_data.get("processed_files", 0),
#                 "progress": cache_data.get("progress", 0),
#             }
#
#         # Initialize and discover files
#         self._set_status("processing", 0)
#         self.discover_files_s3()
#
#         # ✅ Submit background job (non-blocking)
#         executor.submit(self._run_import_job)
#
#         return {
#             "status": "started",
#             "message": f"Background import started for {self.ar_name}",
#             "total_files": self.total_files,
#         }
#
#     # ----------------------------------------------------------------------
#     # Internal import runner
#     # ----------------------------------------------------------------------
#     def _run_import_job(self):
#         """Sequentially process discovered files (background thread)."""
#         try:
#             logger.info(f"🚀 Starting variant import for {self.ar_name}")
#             for idx, (type_name, file_path) in enumerate(self.all_files, start=1):
#                 try:
#                     logger.info(f"Processing file {idx}/{self.total_files}: {file_path}")
#                     handler_class = self.folder_types[type_name]["handler"]
#                     success, message = handler_class().process(
#                         self.analysis_run, file_path
#                     )
#                     if success:
#                         self.processed_files += 1
#                     else:
#                         self._set_status("error", self._update_progress(), error=message)
#                         logger.error(f"Handler failed for {file_path}: {message}")
#                         break
#                 except Exception as e:
#                     logger.error(f"Error processing {file_path}: {e}", exc_info=True)
#                     self._set_status("error", self._update_progress(), error=str(e))
#                     self.analysis_run.status = "failed"
#                     self.analysis_run.save()
#                     return {"status": "error", "error": str(e)}
#
#                 self._update_progress()
#
#             # ✅ Mark complete
#             self._set_status("done", 100)
#             self.analysis_run.status = "completed"
#             self.analysis_run.save()
#             logger.info(f"✅ Variant import completed for {self.ar_name}")
#
#         except Exception as e:
#             logger.critical(f"💥 Fatal error during import: {e}", exc_info=True)
#             self._set_status("error", self._update_progress(), error=str(e))
#             self.analysis_run.status = "failed"
#             self.analysis_run.save()
#
#     # ----------------------------------------------------------------------
#     # Utilities
#     # ----------------------------------------------------------------------
#     def get_progress(self):
#         """Return current progress state from cache."""
#         cache_data = cache.get(self._cache_key())
#         if not cache_data:
#             return {
#                 "status": "not_started",
#                 "progress": 0,
#                 "processed_files": 0,
#                 "total_files": getattr(self, "total_files", 0),
#                 "error": None,
#             }
#
#         total_files = cache_data.get("total_files") or getattr(self, "total_files", 0)
#         processed_files = cache_data.get("processed_files", 0)
#
#         if cache_data.get("status") == "processing":
#             cache_data["progress"] = self._update_progress()
#             cache.set(self._cache_key(), cache_data, timeout=60 * 60)
#
#         cache_data.setdefault("total_files", total_files)
#         cache_data.setdefault("processed_files", processed_files)
#         return cache_data
#
#     def reset_status(self):
#         self._set_status("not_started", 0)
#
#
#

import os
import boto3
import traceback
import logging
from concurrent.futures import ThreadPoolExecutor
from django.conf import settings
from django.core.cache import cache
from analysisrun.models import AnalysisRun, VariantFile
from analysisrun.handlers import AlignmentsFolderHandler, CnvFolderHandler, SnvFolderHandler, CnvAttachmentHandler

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
            "metrics": {"path": "alignments/metrics", "endfix": [
                ".dup_metrics","_Hs_Metrics.txt",".insert_size_metrics.txt","insert_size_histogram.pdf"
            ], "handler": AlignmentsFolderHandler},
            "cnv": {"path": "cnv/output", "endfix": [".cns"],"handler": CnvFolderHandler},
            "cnv_attachments": {"path": "cnv/output", "endfix": ["diagram.pdf", "scatter.png"], "handler": CnvAttachmentHandler},
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
        """
        Scan S3 bucket and find variant files to process.
        Ensures files are always ordered:
        1) _multianno_Filtered.txt
        2) .dup_metrics
        3) .cns
        4) .diagram.pdf
        5) .scatter.png
        """
        self.all_files.clear()
        paginator = self.s3.get_paginator("list_objects_v2")
        discovered_files = []

        # --- Discover all matching files from S3 ---
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
                        discovered_files.append((type_name, full_s3_path))

        # --- Define strict priority by suffix ---
        priority_order = [
            "_multianno_Filtered.txt",  # SNV
            ".dup_metrics",  # Metrics
            ".cns",  # CNV core file
            ".diagram.pdf",  # CNV diagram
            ".scatter.png",  # CNV scatter
        ]

        def sort_key(item):
            _, file_path = item
            file_name = file_path.lower()
            for idx, suffix in enumerate(priority_order):
                if file_name.endswith(suffix.lower()):
                    return (idx, file_name)
            return (len(priority_order), file_name)  # fallback to last

        # --- Sort discovered files deterministically ---
        self.all_files = sorted(discovered_files, key=sort_key)
        # --- Cache and log ---
        self.total_files = len(self.all_files)
        self.processed_files = 0
        self._set_status("processing", 0)

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
                "total_files": self.total_files,  # ✅ Always save total_files
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
                    print(f"Processing file {idx}/{self.total_files}: {file_path}, type: {type_name}")
                    handler_class = self.folder_types[type_name]["handler"]
                    print(handler_class)
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
        """Return current progress, total files, processed count, status, and error (if any)."""
        cache_data = cache.get(self._cache_key())
        if not cache_data:
            return {
                "status": "not_started",
                "progress": 0,
                "processed_files": 0,
                "total_files": getattr(self, "total_files", 0),
                "error": None,
            }

        # Ensure total_files is preserved in cache or fallback to self.total_files
        total_files = cache_data.get("total_files") or getattr(self, "total_files", 0)
        processed_files = cache_data.get("processed_files", 0)

        # If still processing, update progress dynamically
        if cache_data.get("status") == "processing":
            cache_data["progress"] = self._update_progress()
            cache.set(self._cache_key(), cache_data, timeout=60 * 60)

        # Safely include totals
        cache_data.setdefault("total_files", total_files)
        cache_data.setdefault("processed_files", processed_files)

        return cache_data

    def reset_status(self):
        """Reset the status of the import."""
        self._set_status("not_started", 0)
