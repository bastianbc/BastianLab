import os
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

from datetime import date
from django.core.files.base import ContentFile

def save_analysis_run(request):
    if request.method == "POST":
        pipeline     = request.POST.get('pipeline')
        genome       = request.POST.get('genome')
        selected_ids = request.POST.getlist('selected_ids[]')

        run_name     = f"AR_{request.user}_{date.today():%m_%d_%Y}_{genome}_{(int(AnalysisRun.objects.last().id)+1)}"
        csv_filename = f"{run_name}.csv"

        # 1) get or create
        analysis_run, created = AnalysisRun.objects.get_or_create(
            name=run_name,
            defaults={
                'user':       request.user,
                'pipeline':   pipeline,
                'genome':     genome,
                'sheet_name': f"{run_name}",
                'status':     'pending',
            }
        )
        if not created:
            analysis_run.pipeline   = pipeline
            analysis_run.genome     = genome
            analysis_run.sheet_name = f"{run_name}",
            analysis_run.status     = 'pending'
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
