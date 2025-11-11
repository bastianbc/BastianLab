import os
import logging
from pathlib import Path
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import permission_required
from core.decorators import permission_required_for_async
from .serializers import *
from sequencinglib.models import *
from .forms import *
from django.contrib import messages
from django.core.files.base import ContentFile
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from cns.helper import generate_graph
from sheet.views import get_sheet_by_id
from .handlers import *
from .helper import VariantImporter
from variant.models import GVariant
from core.analysis_run_import_logger import S3StorageLogHandler

# logger = logging.getLogger(__name__)


@permission_required("sequencingrun.view_sequencingrun", raise_exception=True)
def analysisruns(request):
    return render(request, "analysisrun_list.html", locals())

@permission_required_for_async("sequencingrun.view_sequencingrun")
def filter_analysisruns(request):
    analysisruns = AnalysisRun().query_by_args(request.user, **request.GET)
    serializer = AnalysisRunSerializer(analysisruns["items"], many=True)
    result = dict()
    result["data"] = serializer.data
    result["draw"] = analysisruns["draw"]
    result["recordsTotal"] = analysisruns["total"]
    result["recordsFiltered"] = analysisruns["count"]

    return JsonResponse(result)

def save_csv_response_to_disk(response, save_path):
    """
    Given a Django HttpResponse (or StreamingHttpResponse) containing CSV,
    write it out to `save_path` (creating directories as needed).
    """
    # 1) Ensure parent directory exists
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    # 2) Grab the raw bytes from the response
    if hasattr(response, "streaming_content"):
        # StreamingHttpResponse
        raw = b"".join(response.streaming_content)
    else:
        # Normal HttpResponse
        raw = response.content

    # 3) Write to disk in binary mode
    with open(save_path, "wb") as f:
        f.write(raw)

def save_analysis_run(request):
    if request.method == "POST":
        pipeline = request.POST.get('pipeline')
        genome = request.POST.get('genome')
        selected_ids = request.POST.getlist('selected_ids[]')
        ar = AnalysisRun()

        run_name = f"{ar.generate_name()}_{pipeline}_{genome}"
        csv_filename = f"{run_name}.csv"
        # 1) get or create
        analysis_run, created = AnalysisRun.objects.get_or_create(
            name=ar.generate_name(),
            defaults={
                'user':       request.user,
                'pipeline':   pipeline,
                'genome':     genome,
                'sheet_name': f"{run_name}",
                'status':     'pending',
            }
        )
        if not created:
            analysis_run.pipeline = pipeline
            analysis_run.genome = genome
            analysis_run.sheet_name = f"{run_name}",
            analysis_run.status = 'pending'
            analysis_run.save(update_fields=['pipeline','genome','sheet_name','status'])

        response = get_sheet_by_id(selected_ids, run_name)

        raw_bytes = (
            b"".join(response.streaming_content)
            if hasattr(response, "streaming_content")
            else response.content
        )
        content_file = ContentFile(raw_bytes)
        analysis_run.sheet.save(csv_filename, content_file, save=True)

        return response


def initialize_import_variants(request, ar_name):
    """
    Renders the import page.
    Does NOT start background import automatically.
    User must click 'Start Import' to begin.
    """
    print("*"*200,"initialize_import_variants")
    # Use ar_name parameter, not hard-coded "AR5"
    GVariant.objects.filter(
        variant_calls__analysis_run__name=ar_name
    ).delete()

    print(f"Deleted variants for {ar_name}")
    print(GVariant.objects.filter(
        variant_calls__analysis_run__name=ar_name
    ))

    AnalysisRun.objects.filter(name=ar_name).update(status="pending")
    VariantFile.objects.filter(analysis_run__name=ar_name).delete()

    importer = VariantImporter(ar_name)
    importer.reset_status()
    importer.discover_files_s3()
    cache_data = importer.get_progress()

    return render(request, "import_variants.html", {
        "analysis_run": ar_name,
        "total_files": importer.total_files,
        "progress": cache_data.get("progress", 0),
        "status": cache_data.get("status", "not_started"),
        "error": cache_data.get("error"),
    })


def start_import_variants(request, ar_name):
    print("-" * 200, "start_import_variants")
    # Attach handler to root logger to capture all logs in this request
    root_logger = logging.getLogger()
    analysis_run = AnalysisRun.objects.get(name=ar_name)
    handler = S3StorageLogHandler(analysis_run.name, analysis_run.sheet_name)
    handler.write_test_log()
    handler.setFormatter(logging.Formatter("[%(asctime)s] %(name)s %(levelname)s: %(message)s"))
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)

    try:
        logging.info(f"=== start_import_variants called for {ar_name} ===")

        GVariant.objects.filter(variant_calls__analysis_run__name=ar_name).delete()
        logging.info(f"Deleted GVariant records for {ar_name}")

        AnalysisRun.objects.filter(name=ar_name).update(status="pending")
        logging.info(f"AnalysisRun {ar_name} set to pending")

        importer = VariantImporter(ar_name)
        importer.discover_files_s3()
        logging.info(f"Discovered {importer.total_files} files")

        result = importer.start_import(force_restart=True)
        logging.info(f"Import started — status={result.get('status')} progress={result.get('progress', 0)}")

        return JsonResponse({
            "analysis_run": ar_name,
            "total_files": importer.total_files,
            "processed_files": result.get("processed_files", 0),
            "progress": result.get("progress", 0),
            "status": result.get("status", "processing"),
            "error": result.get("error", None),
        })

    except Exception as e:
        logging.exception(f"Error in start_import_variants for {ar_name}: {e}")
        return JsonResponse({
            "error": str(e),
            "status": "error",
            "processed_files": 0,
            "progress": 0,
            "total_files": 0,
        })
    finally:
        handler.close()
        root_logger.removeHandler(handler)




def check_import_progress(request, ar_name):
    """
    Poll the current import progress and status.
    This is called repeatedly by the frontend to check progress.
    """
    print("=" * 200,"check_import_progress")
    try:
        importer = VariantImporter(ar_name)
        cache_data = importer.get_progress()

        status = cache_data.get("status", "not_started")
        progress = cache_data.get("progress", 0)
        processed_files = cache_data.get("processed_files", 0)

        return JsonResponse({
            "analysis_run": ar_name,
            "total_files": importer.total_files,
            "processed_files": processed_files,
            "progress": progress,
            "status": status,
            "error": cache_data.get("error", None),
        })
    except Exception as e:
        return JsonResponse({
            "error": str(e),
            "status": "error",
            "processed_files": 0,
            "progress": 0,
            "total_files": 0,
        })


@permission_required_for_async("analysis_run.view_analysisrun")
def report_import_status(request, ar_name):
    analysis_run = AnalysisRun.objects.get(name=ar_name)
    variant_files = VariantFile.objects.filter(analysis_run=analysis_run)

    log_url = S3StorageLogHandler.get_log_path(ar_name)

    files_info = [
        {
            "file_name": file.name,
            "status": file.get_status_display(),
            "log_url": log_url,
        }
        for file in variant_files
    ]

    return JsonResponse(files_info, safe=False)



@permission_required_for_async("analysis_run.delete_analysisrun")
def delete_analysis_run(request,id):
    try:
        ar = AnalysisRun.objects.get(id=id)
        ar.delete()
        messages.success(request,"Analysis Run %s deleted successfully." % ar.name)
        deleted = True
    except Exception as e:
        messages.error(request, "Analysis Run %s not deleted!" % ar.id)
        deleted = False

    return JsonResponse({ "deleted":deleted })


@permission_required("analysis_run.delete_analysisrun",raise_exception=True)
def delete_batch_analysis_run(request):
    try:
        selected_ids = json.loads(request.GET.get("selected_ids"))
        AnalysisRun.objects.filter(id__in=selected_ids).delete()
    except Exception as e:
        print(str(e))
        return JsonResponse({ "deleted":False })

    return JsonResponse({ "deleted":True })



@permission_required_for_async("blocks.delete_blocks")
def check_can_deleted_async(request):
    id = request.GET.get("id")
    instance = AnalysisRun.objects.get(id=id)
    related_objects = []
    for field in instance._meta.related_objects:
        relations = getattr(instance,field.related_name)
        if relations.count() > 0:
            related_objects.append({
                "model": field.related_model.__name__,
                "count": relations.count()
            })

    return JsonResponse({"related_objects":related_objects})
