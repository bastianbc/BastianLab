from django.shortcuts import render
from django.http import JsonResponse
from .service import get_sample_lib_list, generate_file
from samplelib.models import SampleLib
from sequencingrun.models import SequencingRun
from lab.models import Patients
from django.db.models import Case, F, Q, OuterRef, Subquery, Value, When, CharField
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models.functions import Concat
import json
from areas.models import Areas
from sequencingfile.models import SequencingFileSet, SequencingFile
from sequencinglib.models import SequencingLib
from .forms import FilterForm, ReportForm
from .api import query_by_args, _get_authorizated_queryset
from .service import CustomSampleLibSerializer


def filter_sheet(request):
    seq_files = SequencingFile.objects.filter(sequencing_file_set__sample_lib__name="12-12366").values('name', 'checksum').distinct()

    print(seq_files)

    seq_runs = SequencingRun.objects.filter()
    samplelibs = query_by_args(request.user, seq_runs, **request.GET)
    serializer = CustomSampleLibSerializer(samplelibs['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    result['draw'] = samplelibs['draw']
    result['recordsTotal'] = samplelibs['total']
    result['recordsFiltered'] = samplelibs['count']
    return JsonResponse(result)


def get_sheet(request):
    filter = FilterForm()
    filter_report = ReportForm()
    return render(request,"sheet_list.html",locals())


def create_csv_sheet(request):
    # try:
        seq_runs = SequencingRun.objects.filter()
        query_set = query_by_args(request.user, seq_runs, **request.GET)
        # serializer = CustomSampleLibSerializer(query_set, many=True)
        return generate_file(data=query_set, file_name="Analysis Report")
    # except Exception as e:
    #     print(e)
    #     return JsonResponse({'error': str(e)}, status=500)
#
# def create_csv_sheet(request):
#     # print("request"*100)
#     # try:
#         seq_runs = SequencingRun.objects.filter()
#         query_set = _get_authorizated_queryset(seq_runs)
#         print("$"*100)
#         serializer = CustomSampleLibSerializer(query_set, many=True)
#         result = dict()
#         result['data'] = serializer.data
#         print("!"*100)
#         # print("!"*100, serializer.data)
#         return generate_file(data=result, file_name="Analysis Report")
#     # except Exception as e:
#     #     print(e)
#     #     return JsonResponse({'error': str(e)}, status=500)

def sheet_seq_run(request):
    try:
        _seq_run = request.GET['seq_run']
        seq_runs = SequencingRun.objects.filter(id=_seq_run)
        query_set = _get_authorizated_queryset(seq_runs)
        serializer = CustomSampleLibSerializer(query_set['items'], many=True)
        return generate_file(data=serializer.data, file_name=f"Analysis Report_{seq_runs.values('name')}")
    except Exception as e:
        print(e)
        return JsonResponse({'error': str(e)}, status=500)


def sheet_multiple(request):
    selected_ids = json.loads(request.POST.get("selected_ids"))
    seq_runs = SequencingRun.objects.filter(id__in=selected_ids)
    query_set = query_by_args(request.user, seq_runs, **request.GET)
    serializer = CustomSampleLibSerializer(query_set['items'], many=True)
    return generate_file(data=serializer.data, file_name=("_".join([s.name for s in seq_runs]))[:50])


# def sheet_multiple(request):
#     try:
#         selected_ids = json.loads(request.POST.get("selected_ids"))
#         seq_runs = SequencingRun.objects.filter(id__in=selected_ids)
#         serializer = CustomSampleLibSerializer(SampleLib.objects.filter(sl_cl_links__captured_lib__cl_seql_links__sequencing_lib__sequencing_runs__in=seq_runs).distinct(), many=True)
#         return generate_file(request, serializer, "selected_seq_runs")
#     except Exception as e:
#         print(e)
#         return JsonResponse({'error': str(e)}, status=500)