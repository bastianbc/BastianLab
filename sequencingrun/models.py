from django.db import models
from datetime import datetime
from django.db.models import Q, Count
import json


class SequencingRun(models.Model):
    FACILITY_TYPES = (
        ("cat","CAT"),
        ("ihg","IHG"),
        ("broad-institute","Broad Institute"),
        ("other","Other"),
    )

    SEQUENCER_TYPES = (
        ("novaseq-6000-sp","NovaSeq 6000 SP"),
        ("novaseq-6000-s1","NovaSeq 6000 S1"),
        ("novaseq-6000-s2","NovaSeq 6000 S2"),
        ("novaseq-6000-s4","NovaSeq 6000 S4"),
        ("novaseq-x","NovaSeq X"),
        ("hiseq-2500","HiSeq 2500"),
        ("hiseq-4000","HiSeq 4000"),
        ("iseq100","iSeq 100"),
    )

    PE_TYPES = (
        ("PE 50", "PE 50"),
        ("PE 100", "PE 100"),
        ("PE 150", "PE 150"),
        ("SE 150", "SE 150"),
    )

    name = models.CharField(max_length=50, unique=True, verbose_name="Name")
    date_run = models.DateTimeField(default=datetime.now, verbose_name="Date Run")
    date = models.DateTimeField(default=datetime.now, verbose_name="Date")
    facility = models.CharField(max_length=20, choices=FACILITY_TYPES, blank=True, null=True, verbose_name="Facility")
    sequencer = models.CharField(max_length=20, choices=SEQUENCER_TYPES, verbose_name="Sequencer",blank=True, null=True)
    pe = models.CharField(max_length=20, choices=PE_TYPES, verbose_name="PE",blank=True, null=True)
    amp_cycles = models.IntegerField(default=0, verbose_name="AMP Cycles")
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")
    sequencing_libs = models.ManyToManyField("sequencinglib.SequencingLib", blank=True, related_name="sequencing_runs")

    class Meta:
        db_table = "sequencing_run"

    def __str__(self):
        return self.name

    def query_by_args(self, user, **kwargs):
        # print("*" * 100, **kwargs)
        def _get_authorizated_queryset():
            return SequencingRun.objects.all().annotate(num_sequencinglibs=Count("sequencing_libs"))

        def _parse_value(search_value):
            '''
            When the datatables are to be filled with a certain data, the search function of datatables is used.
            The incoming parameter is parsed ve returned. If there is a initial value, the "search_value" has "_initial" prefix.
            Parameters:
                search_value (str): A string
            Returns:
                search_value (str): Parsed value
            '''
            if "_initial:" in search_value:
                return json.loads(search_value.split("_initial:")[1])
            return search_value

        def _is_initial_value(search_value):
            '''
            When the datatables are to be filled with a certain data, the search function of datatables is used.
            The incoming parameter is parsed ve returned. If there is a initial value, the "search_value" has "_initial" prefix.
            Parameters:
                search_value (str): A string
            Returns:
                is_initial (boolean): If there is a initial value, it is True
            '''
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
                if search_value["model"] == "seqlib":
                    queryset = queryset.filter(Q(sequencing_libs__id=search_value["id"]))
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
