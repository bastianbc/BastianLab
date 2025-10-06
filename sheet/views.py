from django.shortcuts import render
from django.http import JsonResponse
from .service import get_sample_lib_list, generate_file
from sequencingrun.models import SequencingRun
import json
from .forms import FilterForm, ReportForm
from .api import query_by_args, _get_authorizated_queryset
from .service import CustomSampleLibSerializer
from datetime import date

def filter_sheet(request):
    seq_runs = SequencingRun.objects.filter()
    samplelibs = query_by_args(request.user, seq_runs, **request.GET)
    serializer = CustomSampleLibSerializer(samplelibs['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    result['draw'] = samplelibs['draw']
    # result['recordsTotal'] = samplelibs['total']
    # result['recordsFiltered'] = samplelibs['count']
    result['recordsTotal'] = 4000
    result['recordsFiltered'] = 10
    return JsonResponse(result)


def get_sheet(request):
    filter = FilterForm()
    filter_report = ReportForm()
    return render(request,"sheet_list.html",locals())


def create_csv_sheet(request):
    print(request)
    try:
        seq_runs = SequencingRun.objects.filter()
        query_set = query_by_args(request.user, seq_runs, **request.GET)
        print(query_set)
        return generate_file(data=query_set, file_name="Analysis Report")
    except Exception as e:
        print(e)
        return JsonResponse({'error': str(e)}, status=500)

def get_sheet_by_id(selected_ids, file_name=None):
    try:
        sequencing_runs = SequencingRun.objects.filter(id__in=selected_ids)
        qs = _get_authorizated_queryset(sequencing_runs)
        return generate_file(data=qs, file_name=file_name)
    except Exception as e:
        print(e)
        return JsonResponse({'error': str(e)}, status=500)

def alternative_export(request):
    try:
        print(request)
        print(request.GET['selected_ids'])
        return
    except Exception as e:
        print(e)
        return JsonResponse({'error': str(e)}, status=500)

def sheet_seq_run(request):
    try:
        _seq_run = request.GET['seq_run']
        seq_runs = SequencingRun.objects.filter(id=_seq_run)
        query_set = query_by_args(request.user, seq_runs, **request.GET)
        return generate_file(data=query_set, file_name=f"Analysis Report_{seq_runs.values('name')}")
    except Exception as e:
        print(e)
        return JsonResponse({'error': str(e)}, status=500)


def sheet_multiple(request):
    selected_ids = json.loads(request.POST.get("selected_ids"))
    seq_runs = SequencingRun.objects.filter(id__in=selected_ids)
    query_set = query_by_args(request.user, seq_runs, **request.GET)
    return generate_file(data=query_set, file_name=("_".join([s.name for s in seq_runs]))[:50])
