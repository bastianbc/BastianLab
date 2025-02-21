from django.db import models
from django.db.models import Q, Count, F, OuterRef, Subquery, Func, Value, CharField, When, Case, Exists
from django.contrib.postgres.aggregates import StringAgg
from django.db.models.functions import Concat

from datetime import datetime
from projects.utils import get_user_projects

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
            '''
            Users can access to some entities depend on their authorize. While the user having admin role can access to all things,
            technicians or researchers can access own projects and other entities related to it.
            '''
            queryset = VariantCall.objects.filter(
                variant_file__name__icontains='BCB037.OMLP-053.HS_Final.annovar.hg19_multianno_Filtered'
                ).annotate(
                    blocks=F('sample_lib__na_sl_links__nucacid__area_na_links__area__block__name'),
                    areas=F('sample_lib__na_sl_links__nucacid__area_na_links__area__name'),
                    genes=F('g_variants__c_variants__gene__name'),
                    patients=F('sample_lib__na_sl_links__nucacid__area_na_links__area__block__patient__pat_id'),
                variant=StringAgg(
                    Case(
                        # First try to get variants where is_alias=True
                        When(
                            Q(
                                Exists(
                                    PVariant.objects.filter(
                                        c_variant__g_variant__variant_call=OuterRef('pk'),
                                        is_alias=True
                                    )
                                )
                            ) & ~Q(
                                Exists(
                                    CVariant.objects.filter(
                                        g_variant__variant_call=OuterRef('pk'),
                                        is_gene_detail=True
                                    )
                                )
                            ),
                            then=PVariant.objects.filter(
                                c_variant__g_variant__variant_call=OuterRef('pk'),
                                is_alias=True
                            ).annotate(
                                combined_value=Concat(
                                        'c_variant__nm_id',
                                        Value(': '),
                                        'name_meta'
                                    )
                                ).values('c_variant__g_variant__variant_call')
                                .annotate(
                                    agg_value=StringAgg('combined_value', delimiter=', ')
                                )
                                .values('agg_value')[:1]
                            ),

                        When(
                            ~Q(
                                Exists(
                                    PVariant.objects.filter(
                                        c_variant__g_variant__variant_call=OuterRef('pk'),
                                        is_alias=True
                                    )
                                )
                            ) & Q(
                                Exists(
                                    CVariant.objects.filter(
                                        g_variant__variant_call=OuterRef('pk'),
                                        is_gene_detail=True
                                    )
                                )
                            ),
                            then=CVariant.objects.filter(
                                g_variant__variant_call=OuterRef('pk'),
                                is_alias=True
                            ).annotate(
                                combined_value=F('gene_detail'),
                            ).values('g_variant__variant_call')
                                .annotate(
                                    agg_value=StringAgg('combined_value', delimiter=', ')
                                )
                                .values('agg_value')[:1]
                        ),
                        default=Value(''),  # Handle case where neither condition matches
                        output_field=CharField()
                    ),
                    delimiter=', ',
                    distinct=True
                ),
                    aliases=StringAgg(
                        Case(
                            # First try to get variants where is_alias=True
                            When(
                                Q(
                                    Exists(
                                        PVariant.objects.filter(
                                            c_variant__g_variant__variant_call=OuterRef('pk'), # 1 (True)
                                            is_alias=False
                                        )
                                    )
                                )
                                & ~Q(
                                    Exists(
                                        CVariant.objects.filter(
                                            g_variant__variant_call=OuterRef('pk'), # 1 (True)
                                            is_gene_detail=True
                                        )
                                    )
                                ),
                                then=PVariant.objects.filter(
                                    c_variant__g_variant__variant_call=OuterRef('pk'),
                                    is_alias=False
                                ).annotate(
                                    combined_value=Concat(
                                        'c_variant__nm_id',
                                        Value(': '),
                                        'name_meta'
                                    )
                                ).values('c_variant__g_variant__variant_call')
                                .annotate(
                                    agg_value=StringAgg('combined_value', delimiter=', ')
                                )
                                .values('agg_value')[:1]
                            ),

                            When(
                                ~Q(
                                    Exists(
                                        PVariant.objects.filter(
                                            c_variant__g_variant__variant_call=OuterRef('pk'),
                                        )
                                    )
                                ) & Q(
                                    Exists(
                                        CVariant.objects.filter(
                                            g_variant__variant_call=OuterRef('pk'),
                                            is_alias=False
                                        )
                                    )
                                ),
                                then=CVariant.objects.filter(
                                    g_variant__variant_call=OuterRef('pk'),
                                    is_alias=False
                                ).annotate(
                                    combined_value=F('gene_detail'),

                                ).values('g_variant__variant_call')
                                .annotate(
                                    agg_value=StringAgg('combined_value', delimiter=', ')
                                )
                                .values('agg_value')[:1]
                            ),
                            default=Value(''),  # Handle case where neither condition matches
                            output_field=CharField()
                        ),
                        delimiter=', ',
                        distinct=True
                    ),
            )
            for gv in queryset:
                print(f"GVariant ID: {gv}, Variants: {gv.variant}, Aliases: {gv.aliases}")

            if not user.is_superuser:
                return queryset.filter(
                    sample_lib__na_sl_links__nucacid__area_na_links__area__block__block_projects__in=get_user_projects(user)
                )

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
            }
            draw = int(kwargs.get('draw', None)[0])
            length = int(kwargs.get('length', None)[0])
            start = int(kwargs.get('start', None)[0])
            search_value = kwargs.get('search[value]', None)[0]
            order_column = kwargs.get('order[0][column]', None)[0]
            order = kwargs.get('order[0][dir]', None)[0]
            patient = kwargs.get('patient', None)[0]
            sample_lib = kwargs.get('sample_lib', None)[0]
            sequencing_run = kwargs.get('sequencing_run', None)[0]
            block = kwargs.get('block', None)[0]
            area = kwargs.get('area', None)[0]
            coverage_value = kwargs.get('coverage', None)[0]
            log2r_value = kwargs.get('log2r', None)[0]
            ref_read_value = kwargs.get('ref_read', None)[0]
            alt_read_value = kwargs.get('alt_read', None)[0]
            variant = kwargs.get('variant', None)[0]
            variant_file = kwargs.get('variant_file', None)[0]


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

            if sequencing_run:
                queryset = queryset.filter(Q(sequencing_run__id=sequencing_run))

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

            if variant:
                queryset = queryset.filter(
                    Q(g_variants__c_variants__p_variants__name_meta__icontains=variant) |
                    Q(g_variants__c_variants__c_var__icontains=variant)  # Ensure `c_name` exists in `CVariant`
                )

            if variant_file:
                queryset = queryset.filter(variant_file__name__icontains=variant_file)

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
    gene = models.ForeignKey("gene.Gene", on_delete=models.CASCADE, related_name="c_variants", blank=True, null=True)
    nm_id = models.CharField(max_length=100, blank=True, null=True)
    c_var = models.CharField(max_length=100, blank=True, null=True)
    exon = models.CharField(max_length=100, blank=True, null=True)
    func = models.CharField(max_length=100, blank=True, null=True)
    gene_detail = models.CharField(max_length=100)
    is_alias = models.BooleanField(default=False)
    is_gene_detail = models.BooleanField(default=False)


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
    is_alias = models.BooleanField(default=False)

    class Meta:
        db_table = "p_variant"

    def update_is_alias(self):
        """Update is_alias based on whether CVariant nm_id matches Gene nm_canonical."""
        if self.c_variant and self.c_variant.gene:
            gene = self.c_variant.gene
            self.is_alias = self.c_variant.nm_id == gene.nm_canonical if gene.nm_canonical else False

    def save(self, *args, **kwargs):
        """Ensure is_alias is updated before saving."""
        self.update_is_alias()
        super().save(*args, **kwargs)

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
