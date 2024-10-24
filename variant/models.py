from django.db import models
from django.db.models import Q, Count

class VariantCall(models.Model):
    sample_lib = models.ForeignKey("samplelib.SampleLib", on_delete=models.CASCADE, related_name="variant_calls", blank=True, null=True)
    sequencing_run = models.ForeignKey("sequencingrun.SequencingRun", on_delete=models.CASCADE, related_name="variant_calls", blank=True, null=True)
    coverage = models.IntegerField(default=0)
    analysis_run = models.ForeignKey("analysisrun.AnalysisRun", on_delete=models.CASCADE, related_name="variant_calls")
    log2r = models.FloatField(default=0.0)
    caller = models.CharField(max_length=30, blank=True, null=True)
    normal_sl = models.ForeignKey("samplelib.SampleLib", on_delete=models.CASCADE, related_name="variant_calls_for_normal", blank=True, null=True)
    label = models.CharField(max_length=30, blank=True, null=True)
    ref_read = models.IntegerField(default=0)
    alt_read = models.IntegerField(default=0)

    class Meta:
        db_table = "variant_call"

    def query_by_args(user, **kwargs):

        def _get_authorizated_queryset():
            return VariantCall.objects.all().annotate()

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
                "1": "ref",
                "2": "pos",
                "3": "alt",
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
                    Q(caller__icontains=search_value) |
                    Q(label__icontains=search_value) |
                    Q(coverage__icontains=search_value)
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

class GVariant(models.Model):
    variant_call = models.ForeignKey(VariantCall, on_delete=models.CASCADE, related_name="g_variants")
    hg = models.IntegerField(default=0)
    chrom = models.CharField(max_length=30, blank=True, null=True)
    start = models.IntegerField(default=0)
    end = models.IntegerField(default=0)
    ref = models.CharField(max_length=30, blank=True, null=True)
    alt = models.CharField(max_length=30, blank=True, null=True)
    avsnp150 = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        db_table = "g_variant"

class CVariant(models.Model):
    g_variant = models.ForeignKey(GVariant, on_delete=models.CASCADE, related_name="c_variants", blank=True, null=True)
    gene = models.CharField(max_length=30, blank=True, null=True)
    nm_id = models.CharField(max_length=30, blank=True, null=True)
    c_var = models.CharField(max_length=30, blank=True, null=True)
    exon = models.CharField(max_length=30, blank=True, null=True)
    func = models.CharField(max_length=30, blank=True, null=True)
    gene_detail = models.CharField(max_length=30)

    class Meta:
        db_table = "c_variant"

class PVariant(models.Model):
    c_variant = models.ForeignKey(CVariant, on_delete=models.CASCADE, related_name="p_variants")
    ref = models.CharField(max_length=30, blank=True, null=True)
    pos = models.CharField(max_length=30, blank=True, null=True)
    alt = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        db_table = "p_variant"
