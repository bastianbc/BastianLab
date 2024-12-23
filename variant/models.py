from django.db import models
from django.db.models import Q, Count, F, OuterRef, Subquery, Func, Value, CharField
from datetime import datetime

class VariantCall(models.Model):
    sample_lib = models.ForeignKey("samplelib.SampleLib", on_delete=models.CASCADE, related_name="variant_calls", blank=True, null=True)
    sequencing_run = models.ForeignKey("sequencingrun.SequencingRun", on_delete=models.CASCADE, related_name="variant_calls", blank=True, null=True)
    variant_file = models.ForeignKey("variant.VariantFile", on_delete=models.CASCADE, related_name="variant_calls", blank=True, null=True)
    coverage = models.IntegerField(default=0)
    analysis_run = models.ForeignKey("analysisrun.AnalysisRun", on_delete=models.CASCADE, related_name="variant_calls")
    log2r = models.FloatField(default=0.0)
    caller = models.CharField(max_length=100, blank=True, null=True)
    normal_sl = models.ForeignKey("samplelib.SampleLib", on_delete=models.CASCADE, related_name="variant_calls_for_normal", blank=True, null=True)
    label = models.CharField(max_length=100, blank=True, null=True)
    ref_read = models.IntegerField(default=0)
    alt_read = models.IntegerField(default=0)

    class Meta:
        db_table = "variant_call"

    def query_by_args(user, **kwargs):

        def _get_authorizated_queryset():
            c_variant_subquery = CVariant.objects.filter(
                g_variant__variant_call=OuterRef('pk')  # Reference the current VariantCall
            ).values('c_var')[:1]

            p_variant_subquery = PVariant.objects.filter(
                c_variant__g_variant__variant_call=OuterRef('pk')  # Reference the current VariantCall
            ).values('name_meta')[:1]
            g_variant_subquery = GVariant.objects.filter(
                variant_call=OuterRef('pk')  # Reference the current VariantCall
            ).values('chrom', 'start', 'end', 'avsnp150')[:1]

            # Concatenate fields to match the required format
            g_variant_annotation = Func(
                Subquery(g_variant_subquery.values('chrom')[:1]),
                Value('-'),
                Subquery(g_variant_subquery.values('start')[:1]),
                Value('-'),
                Subquery(g_variant_subquery.values('end')[:1]),
                Value('-'),
                Subquery(g_variant_subquery.values('avsnp150')[:1]),
                function='CONCAT',
                output_field=CharField()
            )
            return VariantCall.objects.filter().annotate(
                blocks=F('sample_lib__na_sl_links__nucacid__area_na_links__area__block__name'),
                areas = F('sample_lib__na_sl_links__nucacid__area_na_links__area__name'),
                genes = F('g_variants__c_variants__gene__name'),
                patients = F('sample_lib__na_sl_links__nucacid__area_na_links__area__block__patient__pat_id'),
                c_variant = Subquery(c_variant_subquery),
                p_variant = Subquery(p_variant_subquery),
                g_variant=g_variant_annotation
            )

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
            }
            draw = int(kwargs.get('draw', None)[0])
            length = int(kwargs.get('length', None)[0])
            start = int(kwargs.get('start', None)[0])
            search_value = kwargs.get('search[value]', None)[0]
            order_column = kwargs.get('order[0][column]', None)[0]
            order = kwargs.get('order[0][dir]', None)[0]
            patient = kwargs.get('patient', None)[0]
            sample_lib = kwargs.get('sample_lib', None)[0]
            block = kwargs.get('block', None)[0]
            area = kwargs.get('area', None)[0]
            coverage_value = kwargs.get('coverage', None)[0]
            log2r_value = kwargs.get('log2r', None)[0]
            ref_read_value = kwargs.get('ref_read', None)[0]
            alt_read_value = kwargs.get('alt_read', None)[0]


            order_column = ORDER_COLUMN_CHOICES[order_column]
            # django orm '-' -> desc
            if order == 'desc':
                order_column = '-' + order_column

            queryset = _get_authorizated_queryset()

            total = queryset.count()

            is_initial = _is_initial_value(search_value)
            search_value = _parse_value(search_value)


            if sample_lib:
                queryset = queryset.filter(Q(sample_lib__id=sample_lib))

            if area:
                queryset = queryset.filter(
                    Q(sample_lib__na_sl_links__nucacid__area_na_links__area__id=block))

            if block:
                queryset = queryset.filter(
                    Q(sample_lib__na_sl_links__nucacid__area_na_links__area__block_area_links__block__bl_id=block))

            if patient:
                queryset = queryset.filter(
                    Q(sample_lib__na_sl_links__nucacid__area_na_links__area__block__patient__id=patient))
            if coverage_value:
                queryset = queryset.filter(coverage=coverage_value)

            if log2r_value:
                queryset = queryset.filter(log2r=log2r_value)

            if ref_read_value:
                queryset = queryset.filter(ref_read=ref_read_value)

            if alt_read_value:
                queryset = queryset.filter(alt_read=alt_read_value)

            if coverage_value:
                queryset = queryset.filter(coverage=coverage_value)

            if log2r_value:
                queryset = queryset.filter(log2r=log2r_value)

            if ref_read_value:
                queryset = queryset.filter(ref_read=ref_read_value)

            if alt_read_value:
                queryset = queryset.filter(alt_read=alt_read_value)

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
    chrom = models.CharField(max_length=100, blank=True, null=True)
    start = models.IntegerField(default=0)
    end = models.IntegerField(default=0)
    ref = models.CharField(max_length=100, blank=True, null=True)
    alt = models.CharField(max_length=100, blank=True, null=True)
    avsnp150 = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = "g_variant"

class CVariant(models.Model):
    g_variant = models.ForeignKey(GVariant, on_delete=models.CASCADE, related_name="c_variants", blank=True, null=True)
    gene = models.ForeignKey("gene.Gene", on_delete=models.CASCADE, related_name="c_variants")
    nm_id = models.CharField(max_length=100, blank=True, null=True)
    c_var = models.CharField(max_length=100, blank=True, null=True)
    exon = models.CharField(max_length=100, blank=True, null=True)
    func = models.CharField(max_length=100, blank=True, null=True)
    gene_detail = models.CharField(max_length=100)

    class Meta:
        db_table = "c_variant"

class PVariant(models.Model):
    c_variant = models.ForeignKey(CVariant, on_delete=models.CASCADE, related_name="p_variants")
    start = models.IntegerField(default=0)
    end = models.IntegerField(default=0)
    reference_residues = models.CharField(max_length=100, blank=True, null=True)
    inserted_residues = models.CharField(max_length=100, blank=True, null=True)
    change_type = models.CharField(max_length=100, blank=True, null=True)
    name_meta = models.CharField(max_length=100)

    class Meta:
        db_table = "p_variant"

class VariantFile(models.Model):
    FILE_TYPES = [
        ('cns', 'cns'),
        ('variant', "variant")
    ]
    name = models.CharField(max_length=150, blank=True, null=True)
    directory = models.CharField(max_length=200, blank=True, null=True)
    date = models.DateTimeField(default=datetime.now, verbose_name="Date")
    call = models.BooleanField(default=False)
    type = models.CharField(max_length=10, choices=FILE_TYPES, blank=True, null=True)


    class Meta:
        db_table = "variant_file"


class Cns(models.Model):
    sample_lib = models.ForeignKey("samplelib.SampleLib", on_delete=models.CASCADE, related_name="samplelib_cns", blank=True, null=True)
    sequencing_run = models.ForeignKey("sequencingrun.SequencingRun", on_delete=models.CASCADE, related_name="sequencingrun_cns", blank=True, null=True)
    variant_file = models.ForeignKey("variant.VariantFile", on_delete=models.CASCADE, related_name="variantfile_cns", blank=True, null=True)
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
