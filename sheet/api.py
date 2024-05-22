import json
from django.db import models
from datetime import datetime
from django.db.models import Q, F, Count, OuterRef, Subquery, Value, Case, When, CharField
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models.functions import Coalesce, Concat

from samplelib.models import SampleLib, NA_SL_LINK
from lab.models import Patients
from areas.models import Areas
from sequencingfile.models import SequencingFile, SequencingFileSet
from sequencingrun.models import SequencingRun


def _get_authorizated_queryset(seq_runs):
        return SampleLib.objects.filter(
        sl_cl_links__captured_lib__cl_seql_links__sequencing_lib__sequencing_runs__id__in=seq_runs
        ).annotate(
        na_type=F('na_sl_links__nucacid__na_type'),
        seq_run=F('sl_cl_links__captured_lib__cl_seql_links__sequencing_lib__sequencing_runs'),
        patient=F('na_sl_links__nucacid__area_na_links__area__block__patient__pat_id'),
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
       barcode_name=Coalesce('barcode__i5', 'barcode__i7', default=Value(''), output_field=CharField()),
       path=Subquery(
           SequencingFileSet.objects.filter(
               sample_lib=OuterRef('pk'),
               sequencing_run=OuterRef('seq_run')
           ).values('path')[:1]
       ),
       file=ArrayAgg(
           'sequencing_file_sets__sequencing_files__name',
           filter=Q(
               sequencing_file_sets__sample_lib=F('pk'),
               sequencing_file_sets__sequencing_run=F('seq_run')
           ),distinct=True
       ),
       checksum=ArrayAgg(
           'sequencing_file_sets__sequencing_files__checksum',
           filter=Q(
               sequencing_file_sets__sample_lib=F('pk'),
               sequencing_file_sets__sequencing_run=F('seq_run')
           ),distinct=True
       ),
       bait=F("sl_cl_links__captured_lib__bait__name")
    ).distinct().order_by('name')

def _parse_value(search_value):
    if "_initial:" in search_value:
        return json.loads(search_value.split("_initial:")[1])
    return search_value

def _is_initial_value(search_value):
    return "_initial:" in search_value and search_value.split("_initial:")[1] != "null"


def query_by_args(user, seq_runs, **kwargs):
    try:
        ORDER_COLUMN_CHOICES = {
            "0": "id",
            "1": "patient",
            "2": "name",
            "3": "barcode",
            "4": "bait",
            "5": "na_type",
            "6": "area_type",
            "7": "matching_normal_sl",
            "8": "seq_run",
            "9": "file",
            "10": "path",
        }
        if kwargs.get('draw', None) != None:

            draw = int(kwargs.get('draw', None)[0])
            length = int(kwargs.get('length', None)[0])
            start = int(kwargs.get('start', None)[0])
            search_value = kwargs.get('search[value]', None)[0]
            order_column = kwargs.get('order[0][column]', None)[0]
            order = kwargs.get('order[0][dir]', None)[0]
            sequencing_run_filter = kwargs.get('sequencing_run[]', [""])
            patient_filter = kwargs.get('patient', None)[0]
            barcode_filter = kwargs.get('barcode', None)[0]
            bait_filter = kwargs.get('bait', None)[0]
            area_type_filter = kwargs.get('area_type', None)[0]
            na_type_filter = kwargs.get('na_type', None)[0]
            order_column = ORDER_COLUMN_CHOICES[order_column]
            if order == 'desc':
                order_column = '-' + order_column

            queryset = _get_authorizated_queryset(seq_runs)
            total = queryset.count()

            search_value = _parse_value(search_value)
            if sequencing_run_filter[0] != "":
                queryset = queryset.filter(Q(sl_cl_links__captured_lib__cl_seql_links__sequencing_lib__sequencing_runs__id__in=sequencing_run_filter))

            if patient_filter:
                patient = Patients.objects.get(pa_id=patient_filter).pat_id
                queryset = queryset.filter(Q(patient=patient))

            if barcode_filter:
                queryset = queryset.filter(Q(barcode__id=barcode_filter))

            if area_type_filter:
                queryset = queryset.filter(Q(area_type=area_type_filter))

            if na_type_filter:
                queryset = queryset.filter(Q(na_type=na_type_filter))

            if bait_filter:
                queryset = queryset.filter(
                    Q(sl_cl_links__captured_lib__bait__id=bait_filter))

            elif search_value:
                queryset = queryset.filter(
                    Q(name__icontains=search_value)
                )

            count = queryset.count()
            queryset = queryset.order_by(order_column)[start:start + length]
            return {
                'items': queryset,
                'count': count,
                'total': total,
                'draw': draw
            }
        else:
            query_set = _get_authorizated_queryset(seq_runs)
            return _get_authorizated_queryset(seq_runs)

    except Exception as e:
        print(str(e))
        raise