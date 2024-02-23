from django.db import models
from datetime import datetime
from django.db.models import Q, Count, OuterRef, Subquery, Value


class SequencingFileSet(models.Model):
    set_id = models.AutoField(primary_key=True)
    sample_lib = models.ForeignKey("samplelib.SampleLib", on_delete=models.CASCADE, related_name="sequencing_file_sets")
    sequencing_run = models.ForeignKey("sequencingrun.SequencingRun", on_delete=models.CASCADE, related_name="sequencing_file_sets")
    prefix = models.CharField(max_length=250, unique=True) #"Yurif_DNA_GGCTAC"
    path = models.CharField(max_length=1000, blank=True, null=True)
    date_added = models.DateTimeField(blank=True, null=True, auto_now_add=True)


    class Meta:
        db_table = "sequencing_file_set"

    def __str__(self):
        return self.prefix

    def query_by_args(self, user, **kwargs):

        def _get_authorizated_queryset():
            return SequencingFileSet.objects.all().annotate(num_sequencing_files=Count('sequencing_files'))

        def _parse_value(search_value):
            if "_initial:" in search_value:
                v = search_value.split("_initial:")[1]
                return None if v == "null" or not v.isnumeric() else v
            return search_value

        def _is_initial_value(search_value):
            return "_initial:" in search_value and search_value.split("_initial:")[1] != "null"

        try:
            ORDER_COLUMN_CHOICES = {
                "0": "set_id",
                "1": "prefix",
                "2": "path",
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
                queryset = queryset.filter(
                    Q(sequencing_files__file_id=search_value)
                )
            elif search_value:
                queryset = queryset.filter(
                    Q(prefix__icontains=search_value) |
                    Q(path__icontains=search_value)
                )

            count = queryset.count()
            print(count)
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


class SequencingFile(models.Model):
    FILE_TYPES = (
        ("fastq", "Fastq File"),
        ("bam", "Bam File"),
        ("bai", "Bam Bai File"),
    )
    file_id = models.AutoField(primary_key=True)
    sequencing_file_set = models.ForeignKey(SequencingFileSet, on_delete=models.CASCADE, related_name="sequencing_files")
    name = models.CharField(max_length=500, unique=True, verbose_name="File Name")
    checksum = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=10, choices=FILE_TYPES, blank=True, null=True)
    date_added = models.DateTimeField(blank=True, null=True, auto_now_add=True)


    class Meta:
        db_table = "sequencing_file"

    def __str__(self):
        return self.name

    def query_by_args(self, user, **kwargs):

        def _get_authorizated_queryset():
            return SequencingFile.objects.all()

        def _parse_value(search_value):
            if "_initial:" in search_value:
                v = search_value.split("_initial:")[1]
                return None if v == "null" or not v.isnumeric() else v
            return search_value

        def _is_initial_value(search_value):
            return "_initial:" in search_value and search_value.split("_initial:")[1] != "null"

        try:
            ORDER_COLUMN_CHOICES = {
                "0": "file_id",
                "1": "name",
            }
            draw = int(kwargs.get('draw', None)[0])
            print("*"*100,draw)
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
                queryset = queryset.filter(
                    Q(sequencing_file_set__set_id=search_value)
                )
            elif search_value:
                queryset = queryset.filter(
                    Q(name__icontains=search_value) |
                    Q(sequencing_file_set__path__icontains=search_value) |
                    Q(sequencing_file_set__prefix__icontains=search_value)
                )

            count = queryset.count()
            print(count)
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
