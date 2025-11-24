import os
import logging
from datetime import datetime
from analysisrun.models import VariantFile
from cns.models import Cns
from cns.helper import parse_cns_file_with_handler, assign_cnv_attachments
from qc.helper import parse_metrics_files
from variant.helper import variant_file_parser
from variant.models import GVariant, CVariant, PVariant, VariantCall  # lazy import to avoid circulars


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
        self.logger.info(build_file_header(file_path, "metrics"))

        variant_file, _ = VariantFile.objects.get_or_create(
            name=os.path.basename(file_path),
            directory=os.path.dirname(file_path),
            analysis_run=analysis_run,
            type="qc",
            defaults={"status": "processing"},
        )

        success, message, stats = parse_metrics_files(analysis_run, file_path)
        variant_file.status = "completed" if success else "failed"
        variant_file.save()

        status_emoji = "✅" if success else "❌"
        self.logger.info(f"{status_emoji} Completed parsing for {variant_file.name} → {variant_file.status}")
        return success, message


class CnvFolderHandler:
    def __init__(self):
        self.logger = logging.getLogger("cnv_parser")

    def process(self, analysis_run, file_path):
        """Processes and parses CNV (.cns) files and updates VariantFile status."""
        self.logger.info(build_file_header(file_path, "cnv"))
        stats = {}
        try:
            file_name = os.path.basename(file_path)
            directory = os.path.dirname(file_path)

            # --- Create or get VariantFile record ---
            try:
                variant_file, _ = VariantFile.objects.get_or_create(
                    name=file_name,
                    directory=directory,
                    analysis_run=analysis_run,
                    type="cns",
                    defaults={"status": "processing"},
                )
            except Exception as e:
                return False, f"VariantFile creation failed for {file_name}"

            # --- Parse the CNS file ---
            try:
                success, message, stats = parse_cns_file_with_handler(
                    analysis_run=analysis_run,
                    file_path=file_path,
                    variant_file=variant_file,
                )
            except Exception as e:
                variant_file.status = "failed"
                variant_file.save()
                return False, f"CNV parsing failed: {str(e)}"

            # --- Update VariantFile status ---
            variant_file.status = "completed" if success else "failed"
            variant_file.save()


            # --- Logging summary ---
            status_emoji = "✅" if success else "❌"
            summary_msg = f"{status_emoji} CNV file parsed: {variant_file.name} → {variant_file.status}"
            self.logger.info(summary_msg)

            # --- Custom footer for CNS ---
            footer_msg = self.build_cns_footer(
                analysis_run=analysis_run,
                file_name=os.path.basename(file_path),
                stats=stats,
                success=success,
                message=message
            )
            self.logger.info(footer_msg)

            return success, message

        except Exception as e:
            error_msg = f"Critical error in CNV Folder Handler for file {file_path}: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg

    @staticmethod
    def build_cns_footer(analysis_run, file_name=None, stats=None, success=True, message=None):
        """
        Builds a formatted CNV (CNS) parsing summary footer for logs.
        Counts Cns objects related to the given AnalysisRun and displays summary stats.
        """
        line = "=" * 70
        sub_line = "-" * 70
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Count CNS objects linked to this AnalysisRun
        total_cns = Cns.objects.filter(analysis_run=analysis_run).count()

        footer = (
            f"\n{line}\n"
            f"🏁 CNS FILE PARSING SUMMARY — {file_name or 'N/A'}\n"
            f"{sub_line}\n"
            f"📊 CNS Records: {total_cns:>10}\n"
        )

        # Optional parser stats (like total rows, success/fail)
        if stats:
            footer += (
                f"{sub_line}\n"
                f"📊 FILE STATS\n"
                f"{sub_line}\n"
                f"   • Total Rows : {stats.get('total_rows', 'N/A')}\n"
                f"   • Successful : {stats.get('successful', 'N/A')}\n"
                f"   • Failed     : {stats.get('failed', 'N/A')}\n"
            )

        # Optional message
        if message:
            footer += (
                f"{sub_line}\n"
                f"💬 Message: {message}\n"
            )

        status_emoji = "✅" if success else "❌"
        footer += (
            f"{sub_line}\n"
            f"{status_emoji} Completed at: {timestamp}\n"
            f"{line}\n"
        )

        return footer


class CnvAttachmentHandler:
    def __init__(self):
        self.logger = logging.getLogger("cnv_parser")

    def process(self, analysis_run, file_path):
        """Assigns CNV attachment files (.diagram.pdf / .scatter.png) to CNS records."""
        self.logger.info(build_file_header(file_path, "cnv-attachments"))
        stats = {}

        try:
            success, message, stats = assign_cnv_attachments(
                analysis_run=analysis_run,
                file_path=file_path
            )

            status_emoji = "✅" if success else "❌"
            summary_msg = (
                f"{status_emoji} CNV attachment assignment completed: "
                f"{os.path.basename(file_path)} | Updated={stats.get('updated_records', 0)}"
            )
            self.logger.info(summary_msg)

            footer_msg = self.build_cns_attachment_footer(
                analysis_run_name=analysis_run.name,
                file_name=os.path.basename(file_path),
                success=success,
                message=message,
                stats=stats,
            )
            self.logger.info(footer_msg)

            return success, message

        except Exception as e:
            error_msg = f"Critical error in CNV Attachment Handler for file {file_path}: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg

    @staticmethod
    def build_cns_attachment_footer(analysis_run_name, file_name, success, message, stats):
        """Custom footer for CNV attachment logs."""
        status_emoji = "✅" if success else "❌"
        divider = "-" * 70
        return (
            f"\n{divider}\n"
            f"📎 CNS Attachment File: {file_name}\n"
            f"🧩 Analysis Run: {analysis_run_name}\n"
            f"{status_emoji} Status: {'Success' if success else 'Failed'}\n"
            f"📊 Updated Records: {stats.get('updated_records', 'N/A')} / Total: {stats.get('total_records', 'N/A')}\n"
            f"💬 Message: {message}\n"
            f"{divider}\n"
        )



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
        print(success, message, stats)
        variant_file.status = "completed" if success else "failed"
        print("1"*10)
        variant_file.save()
        print("2"*10)

        if success:
            print("3" * 10)
            self.logger.info(f"✅ SNV File processed successfully: {name}")
            self.logger.info(f"📊 Rows: {stats.get('total_rows', 'N/A')} | Success: {stats.get('successful', 'N/A')} | Failures: {stats.get('failed', 'N/A')}")
        else:
            print("4" * 10)
            self.logger.error(f"❌ SNV File failed: {name} | Reason: {message}")

        self.logger.info(self.build_file_footer(
            analysis_run.name,
            file_name=os.path.basename(file_path),
            stats=stats
        ))
        return success, message

    @staticmethod
    def build_file_footer(analysis_run_name, file_name=None, stats=None):
        """
        Builds a prettified footer with DB object counts and optional file-level stats.
        """

        line = "═" * 100
        sub_line = "─" * 100
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("5" * 10)
        # try:
        # Scoped counts per AnalysisRun
        variant_calls = VariantCall.objects.filter(analysis_run__name=analysis_run_name)
        g_variants = GVariant.objects.filter(variant_calls__analysis_run__name=analysis_run_name).distinct()
        c_variants = CVariant.objects.filter(
            g_variant__variant_calls__analysis_run__name=analysis_run_name).distinct()
        p_variants = PVariant.objects.filter(
            c_variant__g_variant__variant_calls__analysis_run__name=analysis_run_name).distinct()
        print("6" * 10)
        footer = (
            f"\n{line}\n"
            f"🏁 FILE PARSING SUMMARY — {file_name or 'N/A'}\n"
            f"{sub_line}\n"
            f"📦 Variant Calls: {variant_calls.count():>10}\n"
            f"🧬 GVariants:     {g_variants.count():>10}\n"
            f"🔗 CVariants:     {c_variants.count():>10}\n"
            f"🧫 PVariants:     {p_variants.count():>10}\n"
        )

        # Optional stats from parser
        if stats:
            footer += (
                f"{sub_line}\n"
                f"📊 FILE STATS\n"
                f"{sub_line}\n"
                f"   • Total Rows : {stats.get('total_rows', 'N/A')}\n"
                f"   • Successful : {stats.get('successful', 'N/A')}\n"
                f"   • Failed     : {stats.get('failed', 'N/A')}\n"
            )
        print("7" * 10)
        footer += (
            f"{sub_line}\n"
            f"✅ Completed at: {timestamp}\n"
            f"{line}\n"
        )
        print("8" * 10)
        # except Exception as e:
        #     footer = (
        #         f"\n{line}\n"
        #         f"⚠️ Error building footer: {e}\n"
        #         f"{line}\n"
        #     )
        return footer
