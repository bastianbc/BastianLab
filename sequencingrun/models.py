from django.db import models
from datetime import datetime
from django.db.models import Q, Count

class SequencingRun(models.Model):
    FACILITY_TYPES = (
        ("type1", "Type 1"),
        ("type2", "Type 2"),
        ("type3", "Type 3"),
    )

    SEQUENCER_TYPES = (
        ("type1", "Type 1"),
        ("type2", "Type 2"),
        ("type3", "Type 3"),
    )

    PE_TYPES = (
        ("type1", "Type 1"),
        ("type2", "Type 2"),
        ("type3", "Type 3"),
    )

    name = models.CharField(max_length=50, unique=True, verbose_name="Name")
    date_run = models.DateTimeField(default=datetime.now, verbose_name="Date Run")
    date = models.DateTimeField(default=datetime.now, verbose_name="Date")
    facility = models.CharField(max_length=20, choices=FACILITY_TYPES, verbose_name="Facility")
    sequencer = models.CharField(max_length=20, choices=SEQUENCER_TYPES, verbose_name="Sequencer")
    pe = models.CharField(max_length=20, choices=SEQUENCER_TYPES, verbose_name="PE")
    amp_cycles = models.IntegerField(default=0, verbose_name="AMP Cycles")
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")
    sequencing_libs = models.ManyToManyField("sequencinglib.SequencingLib", blank=True)

    class Meta:
        db_table = "sequencing_run"

    def __str__(self):
        return self.name

    def query_by_args(self, user, **kwargs):

        def _get_authorizated_queryset():
            queryset = SequencingRun.objects.all()
            if not user.is_superuser:
                return queryset.filter(Q(area__block__project__technician=user) | Q(area__block__project__researcher=user))
            return queryset

        def _parse_value(search_value):
            if "_initial:" in search_value:
                v = search_value.split("_initial:")[1]
                return None if v == "null" or not v.isnumeric() else v
            return search_value

        def _is_initial_value(search_value):
            return "_initial:" in search_value and search_value.split("_initial:")[1] != "null"

        try:
            ORDER_COLUMN_CHOICES = {
                "0": "id",
                "1": "name",
                "2": "date",
                "3": "facility",
                "4": "sequencer",
                "5": "pe",
                "6": "amp_cycles",
                "7": "date_run"
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
                pass
            elif search_value:
                queryset = queryset.filter(
                    Q(name__icontains=search_value) |
                    Q(date__icontains=search_value) |
                    Q(sequencer__icontains=search_value) |
                    Q(facility__icontains=search_value) |
                    Q(date_run__icontains=search_value)
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
