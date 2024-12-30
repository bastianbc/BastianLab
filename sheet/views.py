from django.shortcuts import render
from django.http import JsonResponse
from .service import get_sample_lib_list, generate_file
from sequencingrun.models import SequencingRun
import json
from .forms import FilterForm, ReportForm
from .api import query_by_args, _get_authorizated_queryset
from .service import CustomSampleLibSerializer


def filter_sheet(request):
    seq_runs = SequencingRun.objects.filter()
    print("2")
    samplelibs = query_by_args(request.user, seq_runs, **request.GET)
    print(len(samplelibs['items']))
    print("3")
    serializer = CustomSampleLibSerializer(samplelibs['items'], many=True)
    result = dict()
    print("5")
    result['data'] = serializer.data
    result['draw'] = samplelibs['draw']
    result['recordsTotal'] = samplelibs['total']
    result['recordsFiltered'] = samplelibs['count']
    print(result)
    print("6")
    return JsonResponse(result)


def get_sheet(request):
    filter = FilterForm()
    filter_report = ReportForm()
    return render(request,"sheet_list.html",locals())


def create_csv_sheet(request):
    try:
        seq_runs = SequencingRun.objects.filter()
        query_set = query_by_args(request.user, seq_runs, **request.GET)
        return generate_file(data=query_set, file_name="Analysis Report")
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
    print(request)
    print(request.GET['selected_ids'])
    selected_names = request.POST.get("selected_ids")
    print(selected_names)
    print(type(selected_names))
    seq_runs = SequencingRun.objects.filter(name__in=selected_names)
    query_set = query_by_args(request.user, seq_runs, **request.GET)
    serializer = CustomSampleLibSerializer(query_set['items'], many=True)
    file = generate_file(data=serializer.data, file_name=("_".join([s.name for s in seq_runs]))[:50])
    return generate_file(data=serializer.data, file_name=("_".join([s.name for s in seq_runs]))[:50])
