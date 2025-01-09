from django.db import models
from projects.utils import get_user_projects

class Cns(models.Model):
    sample_lib = models.ForeignKey("samplelib.SampleLib", on_delete=models.CASCADE, related_name="samplelib_cns", blank=True, null=True)
    sequencing_run = models.ForeignKey("sequencingrun.SequencingRun", on_delete=models.CASCADE, related_name="sequencingrun_cns", blank=True, null=True)
    variant_file = models.ForeignKey("variant.VariantFile", on_delete=models.CASCADE, related_name="variantfile_cns", blank=True, null=True)
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
    weight = models.FloatField(default=0.0)

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

        try:
            ORDER_COLUMN_CHOICES = {
                '0': 'id',
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

            if search_value:
                queryset = queryset.filter(
                    Q(id__icontains=search_value) |
                    Q(sample_lib__name__icontains=search_value) |
                    Q(sequencing_run__name__icontains=search_value)
                )

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
