import os
import logging
from datetime import datetime
from analysisrun.models import AnalysisRun, VariantFile
from cns.models import Cns
from cns.helper import parse_cns_file_with_handler
from qc.helper import parse_dup_metrics_with_handler
from variant.helper import variant_file_parser
from core.analysis_run_import_logger import S3StorageLogHandler  # 👈 your S3/local hybrid handler


def build_file_header(file_path, handler_type):
    """Builds a pretty header block for each file being parsed."""
    file_name = os.path.basename(file_path)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = "═" * 90
    return (
        f"\n{line}\n"
        f"📄 FILE PARSER STARTED ({handler_type.upper()})\n"
        f"{line}\n"
        f"🧾 File Name : {file_name}\n"
        f"📂 File Path : {file_path}\n"
        f"⏰ Start Time: {timestamp}\n"
        f"{line}\n"
    )


class AlignmentsFolderHandler:
    def __init__(self):
        self.logger = logging.getLogger("alignments_parser")

    def process(self, analysis_run, file_path):
        self.logger.info(build_file_header(file_path, "alignments"))

        variant_file, _ = VariantFile.objects.get_or_create(
            name=os.path.basename(file_path),
            directory=os.path.dirname(file_path),
            analysis_run=analysis_run,
            type="variant",
            defaults={"status": "processing"},
        )

        success, message = parse_dup_metrics_with_handler(analysis_run, file_path)
        variant_file.status = "completed" if success else "failed"
        variant_file.save()

        status_emoji = "✅" if success else "❌"
        self.logger.info(f"{status_emoji} Completed parsing for {variant_file.name} → {variant_file.status}")
        return success, message


class CnvFolderHandler:
    def __init__(self):
        self.logger = logging.getLogger("cnv_parser")

    def process(self, analysis_run, file_path):
        self.logger.info(build_file_header(file_path, "cnv"))

        variant_file, _ = VariantFile.objects.get_or_create(
            name=os.path.basename(file_path),
            directory=os.path.dirname(file_path),
            analysis_run=analysis_run,
            type="variant",
            defaults={"status": "processing"},
        )

        success, message = parse_cns_file_with_handler(analysis_run, variant_file)
        variant_file.status = "completed" if success else "failed"
        variant_file.save()

        status_emoji = "✅" if success else "❌"
        self.logger.info(f"{status_emoji} CNV file parsed: {variant_file.name} → {variant_file.status}")
        return success, message


class SnvFolderHandler:
    def __init__(self):
        self.logger = logging.getLogger("snv_parser")

    def process(self, analysis_run, file_path):
        self.logger.info(build_file_header(file_path, "snv"))

        name = os.path.basename(file_path)
        directory = os.path.dirname(file_path)

        variant_file, created = VariantFile.objects.get_or_create(
            name=name,
            directory=directory,
            analysis_run=analysis_run,
            type="variant",
            defaults={"status": "processing"},
        )

        if not created and variant_file.status in ["processing", "completed"]:
            self.logger.info(f"⚠️ Skipping already processed file: {name}")
            return True, "Skipped already processed file"

        success, message, stats = variant_file_parser(
            analysis_run=analysis_run,
            file_path=file_path,
            variant_file=variant_file,
        )

        variant_file.status = "completed" if success else "failed"
        variant_file.save()

        if success:
            self.logger.info(f"✅ SNV File processed successfully: {name}")
            self.logger.info(f"📊 Rows: {stats.get('total_rows', 'N/A')} | Success: {stats.get('successful', 'N/A')} | Failures: {stats.get('failed', 'N/A')}")
        else:
            self.logger.error(f"❌ SNV File failed: {name} | Reason: {message}")

        return success, message
