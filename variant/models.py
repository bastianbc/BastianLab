import json
from django.db import models
from django.db.models import Q, F, OuterRef, Value, CharField, When, \
    Case, Exists, ExpressionWrapper, FloatField
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
    variant_meta = models.TextField(blank=True, null=True, help_text="Stores variant information that was previously annotated in queries")
    alias_meta = models.TextField(blank=True, null=True, help_text="Stores alias information that was previously annotated in queries")

    class Meta:
        db_table = "variant_call"

    def query_by_args(user, **kwargs):

        def _get_authorizated_queryset():
            '''
            Users can access to some entities depend on their authorize. While the user having admin role can access to all things,
            technicians or researchers can access own projects and other entities related to it.
            '''
            queryset = VariantCall.objects.filter().annotate(
                blocks=F('sample_lib__na_sl_links__nucacid__area_na_links__area__block__name'),
                areas=F('sample_lib__na_sl_links__nucacid__area_na_links__area__name'),
                genes=F('g_variants__c_variants__gene__name'),
                patients=F('sample_lib__na_sl_links__nucacid__area_na_links__area__block__patient__pat_id'),
                variant=StringAgg(
                    Case(
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
                            ).values('agg_value')[:1]
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
                            ).values('agg_value')[:1]
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
                                combined_value=Concat(
                                    'exon',
                                    Value(': '),
                                    'c_var',
                                    Value("("), "nm_id", Value(")"),
                                ),

                            ).values('g_variant__variant_call')
                            .annotate(
                                agg_value=StringAgg('combined_value', delimiter=', ')
                            ).values('agg_value')[:1]
                        ),
                        default=Value(''),  # Handle case where neither condition matches
                        output_field=CharField()
                    ),
                    delimiter=', ',
                    distinct=True
                ),
            )

            if not user.is_superuser:
                return queryset.filter(
                    sample_lib__na_sl_links__nucacid__area_na_links__area__block__block_projects__in=get_user_projects(user)
                )

            return queryset

        def _get_block_variants_queryset(block_id):
            return VariantCall.objects.filter(sample_lib__na_sl_links__nucacid__area_na_links__area__block__id=block_id).annotate(
                areas=F('sample_lib__na_sl_links__nucacid__area_na_links__area__name'),
                genes=F('g_variants__c_variants__gene__name'),
                p_variant=F('g_variants__c_variants__p_variants__name_meta'),
                vaf=ExpressionWrapper(
                    Case(
                        When(ref_read__gt=0, then=(F('alt_read') * 100.0) / (F('ref_read') + F('alt_read'))),
                        default=Value(0.0),
                        output_field=FloatField(),
                    ),
                    output_field=FloatField()
                )
            ).distinct()

        def _get_area_variants_queryset(area_id):
            return VariantCall.objects.filter(sample_lib__na_sl_links__nucacid__area_na_links__area__id=area_id).annotate(
                genes=F('g_variants__c_variants__gene__name'),
                p_variant=F('g_variants__c_variants__p_variants__name_meta'),
                vaf=ExpressionWrapper(
                    Case(
                        When(ref_read__gt=0, then=(F('alt_read') * 100.0) / (F('ref_read') + F('alt_read'))),
                        default=Value(0.0),
                        output_field=FloatField(),
                    ),
                    output_field=FloatField()
                )
            ).distinct()

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

        def get_kwarg_value(kwargs, key, default=None):
            value = kwargs.get(key, default)
            if isinstance(value, (list, tuple)):
                try:
                    return value[0]
                except IndexError:
                    return default
            return value

        try:
            ORDER_COLUMN_CHOICES = {
                 "0": "id",
                "1": "patient",
                "2": "areas",
                "3": "block",
                "4": "sample_lib",
                "5": "sequencing_run",
                "6": "gene",
                "7": "variant",
                "8": "aliases",
            }
            ORDER_COLUMN_CHOICES_BLOCK = {
                "0": "areas",
                "1": "sample_lib",
                "2": "genes",
                "3": "p_variant",
                "4": "coverage",
                "5": "vaf",
            }
            ORDER_COLUMN_CHOICES_AREA = {
                "0": "sample_lib",
                "1": "genes",
                "2": "p_variant",
                "3": "coverage",
                "4": "vaf",
            }
            draw = int(kwargs.get('draw', None)[0])
            length = int(kwargs.get('length', None)[0])
            start = int(kwargs.get('start', None)[0])
            search_value = kwargs.get('search[value]', None)[0]
            order_column = kwargs.get('order[0][column]', None)[0]
            order = kwargs.get('order[0][dir]', None)[0]
            patient = get_kwarg_value(kwargs, 'patient')
            sample_lib = get_kwarg_value(kwargs, 'sample_lib')
            sequencing_run = get_kwarg_value(kwargs, 'sequencing_run')
            block = get_kwarg_value(kwargs, 'block')
            area = get_kwarg_value(kwargs, 'area')
            coverage_value = get_kwarg_value(kwargs, 'coverage_value')
            log2r_value = get_kwarg_value(kwargs, 'log2r_value')
            ref_read_value = get_kwarg_value(kwargs, 'ref_read_value')
            alt_read_value = get_kwarg_value(kwargs, 'alt_read_value')
            variant = get_kwarg_value(kwargs, 'variant')
            variant_file = get_kwarg_value(kwargs, 'variant_file')
            model_block = get_kwarg_value(kwargs, 'model_block')
            model_area = get_kwarg_value(kwargs, 'model_area')
            block_id = get_kwarg_value(kwargs, 'block_id')
            area_id = get_kwarg_value(kwargs, 'area_id')
            is_initial = _is_initial_value(search_value)
            search_value = _parse_value(search_value)

            # django orm '-' -> desc
            order_column = ORDER_COLUMN_CHOICES_BLOCK[order_column] if model_block else ORDER_COLUMN_CHOICES_AREA[order_column] if model_area else ORDER_COLUMN_CHOICES[order_column]
            # django orm '-' -> desc
            if order == 'desc':
                order_column = '-' + order_column

            if model_block:
                queryset = _get_block_variants_queryset(block_id)
            elif model_area:
                queryset = _get_area_variants_queryset(area_id)
            else:
                queryset = _get_authorizated_queryset()

            total = queryset.count()
            if sample_lib:
                queryset = queryset.filter(Q(sample_lib__id=sample_lib))

            if sequencing_run:
                queryset = queryset.filter(Q(sequencing_run__id=sequencing_run))

            if area:
                queryset = queryset.filter(
                    Q(sample_lib__na_sl_links__nucacid__area_na_links__area__id=block))

            if block:
                queryset = queryset.filter(
                    Q(sample_lib__na_sl_links__nucacid__area_na_links__area__block__id=block))

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
                if search_value["model"] == "block":
                    queryset = queryset.filter(sample_lib__na_sl_links__nucacid__area_na_links__area__block__id=int(search_value["id"]))

                if search_value["model"] == "area":
                    queryset = queryset.filter(sample_lib__na_sl_links__nucacid__area_na_links__area__id=int(search_value["id"]))

            elif search_value:
                queryset = queryset.filter(
                    Q(caller__icontains=search_value) |
                    Q(label__icontains=search_value) |
                    Q(coverage__icontains=search_value)
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
    is_alias = models.BooleanField(default=False) # if c_variant.nm_id == to gene.nm_id set True
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
        ('variant', "variant"),
        ('qc', "qc")
    ]
    name = models.CharField(max_length=150, blank=True, null=True)
    directory = models.CharField(max_length=200, blank=True, null=True)
    date = models.DateTimeField(default=datetime.now, verbose_name="Date")
    call = models.BooleanField(default=False)
    type = models.CharField(max_length=10, choices=FILE_TYPES, blank=True, null=True)


    class Meta:
        db_table = "variant_file"

    def __str__(self):
        return self.name

class VariantsView(models.Model):
    area_id = models.IntegerField()
    area_name = models.CharField(max_length=50)
    area_type = models.IntegerField(null=True)
    collection = models.CharField(max_length=2)
    block_id = models.IntegerField()
    block_name = models.CharField(max_length=50)
    samplelib_id = models.IntegerField()
    samplelib_name = models.CharField(max_length=50)
    gene_id = models.IntegerField()
    gene_name = models.CharField(max_length=30)
    chromosome = models.CharField(max_length=30, null=True)
    variantcall_id = models.IntegerField()
    analysis_run_id = models.IntegerField()
    analysis_run_name = models.IntegerField()
    coverage = models.IntegerField()
    log2r = models.FloatField()
    caller = models.CharField(max_length=100, null=True)
    ref_read = models.IntegerField()
    alt_read = models.IntegerField()
    vaf = models.FloatField()
    alias = models.CharField(max_length=50, null=True)
    variant = models.CharField(max_length=50, null=True)
    gvariant_id = models.IntegerField()
    g_chromosome = models.CharField(max_length=100, null=True)
    g_start = models.IntegerField()
    g_end = models.IntegerField()
    g_ref = models.CharField(max_length=100, null=True)
    g_alt = models.CharField(max_length=100, null=True)
    avsnp150 = models.CharField(max_length=100, null=True)
    cvariant_id = models.IntegerField()
    nm_id = models.CharField(max_length=100, null=True)
    c_var = models.CharField(max_length=100, null=True)
    exon = models.CharField(max_length=100, null=True)
    func = models.CharField(max_length=100, null=True)
    pvariant_id = models.IntegerField(null=True)
    reference_residues = models.CharField(max_length=100, null=True)
    inserted_residues = models.CharField(max_length=100, null=True)
    change_type = models.CharField(max_length=100, null=True)

    class Meta:
        managed = False
        db_table = 'variants_view'

    def query_by_args(self, **kwargs):
        try:
            ORDER_COLUMN_CHOICES = {
                "0": "id",
                "1": "patient",
                "2": "areas",
                "3": "block",
                "4": "sample_lib",
                "5": "sequencing_run",
                "6": "gene",
                "7": "variant",
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

            queryset = VariantsView.objects.filter(is_superuser=False)

            total = queryset.count()

            total = queryset.count()
            if sample_lib:
                queryset = queryset.filter(Q(sample_lib__id=sample_lib))

            if sequencing_run:
                queryset = queryset.filter(Q(sequencing_run__id=sequencing_run))

            if area:
                queryset = queryset.filter(
                    Q(sample_lib__na_sl_links__nucacid__area_na_links__area__id=block))

            if block:
                queryset = queryset.filter(
                    Q(sample_lib__na_sl_links__nucacid__area_na_links__area__block__id=block))

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

            if search_value:
                queryset = queryset.filter(
                    Q(patient__icontains=search_value) |
                    Q(area__icontains=search_value) |
                    Q(last_name__icontains=search_value)
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
