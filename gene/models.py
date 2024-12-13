from django.db import models
from django.db.models import Q, Count

class Gene(models.Model):
    gene_id = models.IntegerField(default=0)
    name = models.CharField(max_length=30, verbose_name="Name", unique=True)
    full_name = models.CharField(max_length=30, verbose_name="Name", blank=True, null=True)
    chr = models.CharField(max_length=30, verbose_name="Chromosome", blank=True, null=True)
    start = models.IntegerField(default=0)
    end = models.IntegerField(default=0)
    hg = models.CharField(max_length=30, verbose_name="HG", blank=True, null=True)
    type = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        db_table = "gene"

    def __str__(self):
        return self.name

    def query_by_args(user, **kwargs):

        def _get_authorizated_queryset():
            return Gene.objects.all().annotate()

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
                "2": "chr",
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
                # filter = [sequencing_run.id for sequencing_run in SequencingRun.objects.filter(id=search_value)]
                # queryset = queryset.filter(Q(id__in=filter))
                pass
            elif search_value:
                queryset = queryset.filter(
                    Q(name__icontains=search_value) |
                    Q(chr__icontains=search_value)
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
