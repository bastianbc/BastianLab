from django.db import models
from datetime import datetime
from django.db.models import Q, Count, OuterRef, Subquery, Value

class SequencingFile(models.Model):
    sample_lib = models.ForeignKey("samplelib.SampleLib", on_delete=models.CASCADE, related_name="sequencing_files")
    folder_name = models.CharField(max_length=100, blank=True, null=True)
    read1_file = models.CharField(max_length=100, blank=True, null=True)
    read1_checksum = models.CharField(max_length=100, blank=True, null=True)
    read1_count = models.IntegerField(default=0, blank=True, null=True)
    read2_file = models.CharField(max_length=100, blank=True, null=True)
    read2_checksum = models.CharField(max_length=100, blank=True, null=True)
    read2_count = models.IntegerField(default=0, blank=True, null=True)
    is_read_count_equal = models.BooleanField(default=False, blank=True, null=True)
    path = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        db_table = "sequencing_file"

    def __str__(self):
        return self.path if self.path else ""

    def save(self, *args, **kwargs):

        self.read1_count = SampleLib.objects.filter()
        self.read2_count = slugify(self.title)
        super(SequencingFile, self).save(*args, **kwargs)

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
                "0": "id",
                "1": "folder_name",
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
                    Q(folder_name__icontains=search_value) |
                    Q(read1_file__icontains=search_value) |
                    Q(read1_checksum__icontains=search_value) |
                    Q(read1_count__icontains=search_value) |
                    Q(read2_file__icontains=search_value) |
                    Q(read2_checksum__icontains=search_value) |
                    Q(read2_count__icontains=search_value) |
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
