import os
from pathlib import Path
from django.views.decorators.csrf import csrf_exempt
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
from .helper import handle_variant_file , parse_cns_file
from cns.helper import generate_graph





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
        try:
            if form.is_valid():
                analysis_run = form.save(commit=False)

                sheet_content = form.cleaned_data['sheet_content']

                # convert to csv
                csv_file = ContentFile(sheet_content.encode('utf-8'))
                file_name = f"{analysis_run.user.username}_analysis_sheet.csv"
                analysis_run.sheet_name = file_name
                analysis_run.save()
                analysis_run.sheet.save(file_name, csv_file, save=False)
                analysis_run.save()
        except:
            return JsonResponse({"success": True})
    return JsonResponse({"success": True})

@csrf_exempt
def process_variant(request, variant_type, ar_name):
    variant_paths={
        'CNV':'cnv',
        'SNV':'snv',
        'SV':'sv'
    }
    if request.method == 'POST':
        try:

            file_path= handle_variant_file(ar_name, variant_paths[variant_type])

            parse_cns_file(file_path, ar_name)
            print("Parsing complete" , file_path)

            graphic = generate_graph(ar_name, file_path)
            print("Graph generated" , graphic)

            response = JsonResponse({'success': True, 'graphic': graphic})


            return response
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        

@csrf_exempt
def import_cns(request, ar_name):
    if request.method == 'POST':
        try:
            folders = ['cnv\output', 'snv\output', 'sv\output']
            cns_files = []
            cns_objects_created = 0
            files_parsed = 0

            for folder in folders:
                    files = handle_variant_file(ar_name,folder)
                    print(files)
                    cns_files.extend(files)
                    files_parsed += len(files)
                    for file in files:
                        parse_cns_file(file, ar_name)
                        cns_objects_created += 1

            cns_object_location = f'/path/to/cns/objects/{ar_name}'
            files_location = f'/path/to/ar/{ar_name}'

            response = JsonResponse({
                'success': True,
                'cnsObjectsCreated': cns_objects_created,
                'filesParsed': files_parsed,
                'cnsObjectLocation': cns_object_location,
                'filesLocation': files_location
            })

            return response
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})