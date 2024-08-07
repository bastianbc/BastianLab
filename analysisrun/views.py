from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import permission_required
from core.decorators import permission_required_for_async
from .serializers import *
from sequencinglib.models import *
from .forms import *
from django.contrib import messages

@permission_required("sequencingrun.view_sequencingrun",raise_exception=True)
def analysisruns(request):
    return render(request, "analysisrun_list.html", locals())

@permission_required_for_async("sequencingrun.view_sequencingrun")
def filter_analysisruns(request):
    analysisruns = AnalysisRun().query_by_args(request.user,**request.GET)
    serializer = AnalysisRunSerializer(analysisruns['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    result['draw'] = analysisruns['draw']
    result['recordsTotal'] = analysisruns['total']
    result['recordsFiltered'] = analysisruns['count']

    return JsonResponse(result)

def save_analysis_run(request):
    if request.method == "POST":
        form = AnalysisRunForm(request.POST)
        if form.is_valid():
            analysis_run = form.save(commit=False)

            sheet_content = form.cleaned_data['sheet_content']

            # convert to csv
            csv_file = ContentFile(sheet_content.encode('utf-8'))
            file_name = f"{analysis_run.user.username}_analysis_sheet.csv"

            analysis_run.sheet.save(file_name, csv_file, save=False)

            analysis_run.save()

            return JsonResponse({"success": True})
    return JsonResponse({"success": False})
