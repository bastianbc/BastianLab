from django.db import models
from projects.utils import get_user_projects
from django.db.models import Q
import json


class Cns(models.Model):
    sample_lib = models.ForeignKey("samplelib.SampleLib", on_delete=models.CASCADE, related_name="samplelib_cns", blank=True, null=True)
    sequencing_run = models.ForeignKey("sequencingrun.SequencingRun", on_delete=models.CASCADE, related_name="sequencingrun_cns", blank=True, null=True)
    variant_file = models.ForeignKey("variant.VariantFile", on_delete=models.CASCADE, related_name="variant_file_cns", blank=True, null=True)
    analysis_run = models.ForeignKey("analysisrun.AnalysisRun", on_delete=models.CASCADE, related_name="analysis_run_cns")
    chromosome = models.CharField(max_length=20, blank=True, null=True)
    start = models.IntegerField(default=0, blank=True, null=True)
    end = models.IntegerField(default=0, blank=True, null=True)
    gene = models.CharField(max_length=500, blank=True, null=True)
    depth = models.FloatField(default=0.0)
    ci_hi = models.FloatField(default=0.0)
    ci_lo = models.FloatField(default=0.0)
    cn = models.FloatField(default=0.0)
    log2 = models.FloatField(default=0.0)
    p_bintest = models.FloatField(default=0.0)
    p_ttest = models.FloatField(default=0.0)
    probes = models.FloatField(default=0.0)
    weight = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        db_table = "cns"

    def query_by_args(self, user, **kwargs):
        def _get_authorizated_queryset():
            queryset = Cns.objects.all()
            if not user.is_superuser:
                return queryset.filter(
                    sample_lib__na_sl_links__nucacid__area_na_links__area__block__block_projects__in=get_user_projects(user)
                )

            return queryset

        def _parse_value(search_value):
            if "_initial:" in search_value:
                return json.loads(search_value.split("_initial:")[1])

            return search_value

        def _is_initial_value(search_value):
            return "_initial:" in search_value and search_value.split("_initial:")[1] != "null"

        try:
            ORDER_COLUMN_CHOICES = {
                '0': 'id',
                '1': 'sample_lib',
                '2': 'sequencing_run',
                '4': 'chromosome',
                '5': 'start',
                '6': 'end',
                '7': 'log2',
            }
            print(
                kwargs.get('draw', None),
            )
            draw = int(kwargs.get('draw', None)[0])
            length = int(kwargs.get('length', None)[0])
            start = int(kwargs.get('start', None)[0])
            search_value = kwargs.get('search[value]', None)[0]

            log2_filter = kwargs.get('log2', None)[0]
            start_filter = kwargs.get('chr_start', None)[0]
            end_filter = kwargs.get('chr_end', None)[0]
            sequencing_run_filter = kwargs.get('sequencing_run', None)[0]
            sample_library_filter = kwargs.get('sample_library', None)[0]
            chromosome_filter = kwargs.get('chromosome', None)[0]
            gene_filter = kwargs.get('gene', None)[0]
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

            if search_value:
                queryset = queryset.filter(
                    Q(id__icontains=search_value) |
                    Q(sample_lib__name__icontains=search_value) |
                    Q(sequencing_run__name__icontains=search_value)
                )
            if log2_filter:
                queryset = queryset.filter(Q(log2__gte=log2_filter) | Q(log2__lte=-int(log2_filter)))

            if start_filter:
                queryset = queryset.filter(Q(start__gte=start_filter))

            if end_filter:
                queryset = queryset.filter(Q(end__lte=end_filter))

            if sequencing_run_filter:
                queryset = queryset.filter(Q(sequencing_run__id=sequencing_run_filter))

            if sample_library_filter:
                queryset = queryset.filter(Q(sample_lib__id=sample_library_filter))

            if chromosome_filter:
                queryset = queryset.filter(Q(chromosome__icontains=chromosome_filter))

            if gene_filter:
                queryset = queryset.filter(Q(gene__icontains=gene_filter))

            count = queryset.count()
            queryset = queryset.order_by(order_column)[start:start + length]
            return {
                'items': queryset,
                'count': count,
                'total': total,
                'draw': draw
            }
        except Exception as e:
            print(str(e))
            raise
