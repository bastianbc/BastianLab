from django.shortcuts import render
from django.http import JsonResponse
from .service import get_sample_lib_list, CustomSampleLibSerializer, generate_file
from samplelib.models import SampleLib
from sequencingrun.models import SequencingRun
from lab.models import Patients
from django.db.models import Case, CharField, F, OuterRef, Subquery, Value, When
import json
from areas.models import Areas
from sequencinglib.models import SequencingLib
from capturedlib.models import CapturedLib

def _get_queryset(seq_runs):
    query_set = SampleLib.objects.filter(
        sl_cl_links__captured_lib__cl_seql_links__sequencing_lib__sequencing_runs__id__in=seq_runs).annotate(
        na_type=F('na_sl_links__nucacid__na_type'),
        seq_run=Subquery(
            SequencingRun.objects.filter(
                sequencing_libs__cl_seql_links__captured_lib__sl_cl_links__sample_lib=OuterRef('pk'),
                id__in=seq_runs
            ).values('name')[:1]
        ),
        patient=Subquery(
            Patients.objects.filter(
                patient_blocks__block_areas__area_na_links__nucacid__na_sl_links__sample_lib=OuterRef('pk')
            ).values('pat_id')[:1]
        ),
        sex=Subquery(
            Patients.objects.filter(
                patient_blocks__block_areas__area_na_links__nucacid__na_sl_links__sample_lib=OuterRef('pk')
            ).values('sex')[:1]
        ),
        area_type=Subquery(
            Areas.objects.filter(
                area_na_links__nucacid__na_sl_links__sample_lib=OuterRef('pk')
            ).annotate(
                simplified_area_type=Case(
                    When(area_type='normal', then=Value('normal')),
                    When(area_type__isnull=True, then=Value(None)),  # Exclude None explicitly if needed
                    default=Value('tumor'),
                    output_field=CharField(),
                )
            ).values('simplified_area_type')[:1]
        ),
        matching_normal_sl=Case(
            When(
                area_type=Value('normal'),
                then=Value(None)
            ),
            default=Subquery(
                SampleLib.objects.filter(
                    na_sl_links__nucacid__area_na_links__area__area_type='normal',
                    na_sl_links__nucacid__area_na_links__area__block__patient=OuterRef(
                        "na_sl_links__nucacid__area_na_links__area__block__patient")
                ).values('name')[:1]
            ),
            output_field=CharField()
        ),
        barcode_name=F('barcode__name')
    ).distinct().order_by('name')
    return query_set

def filter_sheet(request):
    result = get_sample_lib_list(request)
    return JsonResponse(result)


def get_sheet(request):
    return render(request,"sheet_list.html",locals())


def create_csv_sheet(request):
    try:
        seq_runs = SequencingRun.objects.filter()
        query_set = _get_queryset(seq_runs)
        return generate_file(data=query_set, file_name="all_seq_runs")
    except Exception as e:
        print(e)
        return JsonResponse({'error': str(e)}, status=500)

def sheet_seq_run(request,id):
    try:
        seq_runs = SequencingRun.objects.filter(id=id)
        query_set = _get_queryset([id])
        return generate_file(data=query_set, file_name=("_".join([s.name for s in seq_runs]))[:50])
    except Exception as e:
        print(e)
        return JsonResponse({'error': str(e)}, status=500)


def sheet_multiple(request):
    selected_ids = json.loads(request.POST.get("selected_ids"))
    seq_runs = SequencingRun.objects.filter(id__in=selected_ids)
    query_set = _get_queryset(seq_runs)
    return generate_file(data=query_set, file_name=("_".join([s.name for s in seq_runs]))[:50])


# def sheet_multiple(request):
#     try:
#         selected_ids = json.loads(request.POST.get("selected_ids"))
#         seq_runs = SequencingRun.objects.filter(id__in=selected_ids)
#         serializer = CustomSampleLibSerializer(SampleLib.objects.filter(sl_cl_links__captured_lib__cl_seql_links__sequencing_lib__sequencing_runs__in=seq_runs).distinct(), many=True)
#         return generate_file(request, serializer, "selected_seq_runs")
#     except Exception as e:
#         print(e)
#         return JsonResponse({'error': str(e)}, status=500)