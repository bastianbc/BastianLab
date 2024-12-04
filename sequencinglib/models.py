from django.db import models
from datetime import datetime
from django.db.models import Q, Count
from core.validators import validate_name_contains_space
import json

class SequencingLib(models.Model):
    BUFFER_TYPES = (
        ("low-te", "Low TE"),
        ("te", "TE"),
        ("buffer-eb", "Buffer EB"),
        ("water", "Water"),
    )

    name = models.CharField(max_length=50, unique=True, validators=[validate_name_contains_space], verbose_name="Name")
    date = models.DateTimeField(default=datetime.now, verbose_name="Date")
    nmol = models.FloatField(default=0, verbose_name="N Mol")
    target_vol = models.FloatField(default=0, verbose_name="Target Volume")
    buffer = models.CharField(max_length=20, choices=BUFFER_TYPES, verbose_name="Buffer")
    pdf = models.FileField(upload_to="uploads/", null=True, blank=True)
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")

    class Meta:
        db_table = "sequencing_lib"

    def __str__(self):
        return self.name

    def query_by_args(self, user, **kwargs):

        def _get_authorizated_queryset():
            return SequencingLib.objects.all().annotate(
                num_capturedlibs=Count("cl_seql_links"),
                num_sequencingruns=Count("sequencing_runs",distinct=True)
            )

        def _parse_value(search_value):
            if "_initial:" in search_value:
                return json.loads(search_value.split("_initial:")[1])
            return search_value

        def _is_initial_value(search_value):
            return "_initial:" in search_value and search_value.split("_initial:")[1] != "null"

        try:
            ORDER_COLUMN_CHOICES = {
                "0": "id",
                "1": "name",
                "2": "date",
                "3": "nmol",
                "4": "buffer",
            }
            draw = int(kwargs.get('draw', None)[0])
            length = int(kwargs.get('length', None)[0])
            start = int(kwargs.get('start', None)[0])
            search_value = kwargs.get('search[value]', None)[0]
            order_column = kwargs.get('order[0][column]', None)[0]
            order = kwargs.get('order[0][dir]', None)[0]

            order_column = ORDER_COLUMN_CHOICES[order_column]
            # django orm '-' -> desc
            if order == 'desc':
                order_column = '-' + order_column

            queryset = _get_authorizated_queryset()

            total = queryset.count()

            is_initial = _is_initial_value(search_value)
            search_value = _parse_value(search_value)
            if is_initial:
                if search_value["model"] == "sequencing_run":
                    queryset = queryset.filter(Q(sequencing_runs__id=search_value["id"]))
                if search_value["model"] == "captured_lib":
                    filter = [cl_seql_link.sequencing_lib.id for cl_seql_link in CL_SEQL_LINK.objects.filter(captured_lib__id=search_value["id"])]
                    queryset = queryset.filter(Q(id__in=filter))
            elif search_value:
                queryset = queryset.filter(
                    Q(name__icontains=search_value) |
                    Q(date__icontains=search_value)
                )

            count = queryset.count()
            queryset = queryset.order_by(order_column)[start:start + length]
            # queryset = queryset[start:start + length]
            return {
                'items': queryset,
                'count': count,
                'total': total,
                'draw': draw
            }
        except Exception as e:
            print(str(e))
            raise

class CL_SEQL_LINK(models.Model):
    sequencing_lib = models.ForeignKey(SequencingLib,on_delete=models.CASCADE, verbose_name="Sequencing Library", related_name="cl_seql_links")
    captured_lib = models.ForeignKey("capturedlib.CapturedLib", on_delete=models.CASCADE, verbose_name="Captured Library", related_name="cl_seql_links")
    volume = models.FloatField(default=0, verbose_name="Volume")
    date = models.DateTimeField(default=datetime.now, verbose_name="Date")

    class Meta:
        db_table = "cl_seql_link"
