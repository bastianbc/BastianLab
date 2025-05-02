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

def save_analysis_run(request):
    if request.method == "POST":
        # try:
            print(request.POST)
            pipeline = request.POST.get('pipeline')  # returns 'v1'
            genome = request.POST.get('genome')  # returns 'hg19'
            selected_ids = request.POST.getlist('selected_ids[]')  # returns ['268', '261', '264', '266', '269']

            # pipeline = json.dumps(request.POST["pipeline"][0])
            # genome = json.dumps(request.POST["genome"][0])
            # selected_ids = json.dumps(request.POST["selected_ids[]"][0])
            print(pipeline, genome, selected_ids)
            print(type(pipeline), type(genome), type(selected_ids))
            return get_sheet_by_id(selected_ids)
            print(sheet)
            print(type(sheet))
            AnalysisRun.objects.create(
                user=request.user,
                name=f"AR_{date.today().strftime('%Y_%m_%d')}",
                pipeline=pipeline,
                genome=genome,
                sheet=sheet,
                sheet_name=f"AR_{date.today().strftime('%Y_%m_%d')}",
                status="pending"
            )
            print("Analysis Run Saved")
        # except Exception as e:
        #     print(f"{str(e)}"*10)
        #     return JsonResponse({"success": False})
    return JsonResponse({"success": True})
