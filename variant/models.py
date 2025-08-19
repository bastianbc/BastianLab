import json
from django.db import models
from django.db.models import (Q, F, OuterRef, Value, CharField, IntegerField, Count, Subquery,
                              When, Case, Exists, ExpressionWrapper, FloatField)
from django.contrib.postgres.aggregates import StringAgg
from django.db.models.functions import Concat
from datetime import datetime
from projects.utils import get_user_projects
from django.db.models.functions import Coalesce

class GVariant(models.Model):
    hg = models.IntegerField(default=0)
    chrom = models.CharField(max_length=100, blank=True, null=True)
    start = models.IntegerField(default=0)
    end = models.IntegerField(default=0)
    ref = models.CharField(max_length=100, blank=True, null=True)
    alt = models.CharField(max_length=100, blank=True, null=True)
    avsnp150 = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = "g_variant"
        # unique_together = ['chrom', 'start', 'end', 'ref', 'alt']

    @staticmethod
    def query_by_args(user, **kwargs):
        """
        Query GVariant objects with filtering, pagination, and authorization.
        This method handles DataTables requests and filters variants based on user permissions.
        """

        def _get_authorizated_queryset():
            """
            Users can access entities based on their authorization. Admin users can access everything,
            while technicians or researchers can only access their own projects and related entities.
            """
            qs = (
                GVariant.objects
                .annotate(
                    blocks=F('variant_calls__sample_lib__na_sl_links__nucacid__area_na_links__area__block__name'),
                    areas=F('variant_calls__sample_lib__na_sl_links__nucacid__area_na_links__area__name'),
                    genes=F('c_variants__gene__name'),
                    patients=F(
                        'variant_calls__sample_lib__na_sl_links__nucacid__area_na_links__area__block__patient__pat_id'),
                )
                .order_by('id')  # highest COSMIC count first, then id
                .distinct()
            )

            if not user.is_superuser:
                qs = qs.filter(
                    variant_calls__sample_lib__na_sl_links__nucacid__area_na_links__area__block__block_projects__in=get_user_projects(
                        user)
                )

            return qs

        def _get_block_variants_queryset(block_id):
            """
            Get GVariant queryset filtered by specific block ID with additional annotations.
            """
            return GVariant.objects.filter(
                variant_calls__sample_lib__na_sl_links__nucacid__area_na_links__area__block__id=block_id
            ).annotate(
                areas=F('variant_calls__sample_lib__na_sl_links__nucacid__area_na_links__area__name'),
                genes=F('c_variants__gene__name'),
                p_variant=F('c_variants__p_variants__name_meta'),
                coverage=F('variant_calls__coverage'),
                vaf=ExpressionWrapper(
                    Case(
                        When(variant_calls__ref_read__gt=0,
                             then=(F('variant_calls__alt_read') * 100.0) / (F('variant_calls__ref_read') + F('variant_calls__alt_read'))),
                        default=Value(0.0),
                        output_field=FloatField(),
                    ),
                    output_field=FloatField()
                ),
                sample_lib=F('variant_calls__sample_lib'),
                sequencing_run=F('variant_calls__sequencing_run'),
                variant_file=F('variant_calls__variant_file'),
                log2r=F('variant_calls__log2r'),
                caller=F('variant_calls__caller'),
                ref_read=F('variant_calls__ref_read'),
                alt_read=F('variant_calls__alt_read'),
                analysis_run=F('variant_calls__analysis_run')
            ).distinct()

        def _get_area_variants_queryset(area_id):
            """
            Get GVariant queryset filtered by specific area ID with additional annotations.
            """
            return GVariant.objects.filter(
                variant_calls__sample_lib__na_sl_links__nucacid__area_na_links__area__id=area_id
            ).annotate(
                genes=F('c_variants__gene__name'),
                p_variant=F('c_variants__p_variants__name_meta'),
                coverage=F('variant_calls__coverage'),
                vaf=ExpressionWrapper(
                    Case(
                        When(variant_calls__ref_read__gt=0,
                             then=(F('variant_calls__alt_read') * 100.0) / (F('variant_calls__ref_read') + F('variant_calls__alt_read'))),
                        default=Value(0.0),
                        output_field=FloatField(),
                    ),
                    output_field=FloatField()
                ),
                sample_lib=F('variant_calls__sample_lib'),
                sequencing_run=F('variant_calls__sequencing_run'),
                variant_file=F('variant_calls__variant_file'),
                log2r=F('variant_calls__log2r'),
                caller=F('variant_calls__caller'),
                ref_read=F('variant_calls__ref_read'),
                alt_read=F('variant_calls__alt_read'),
                analysis_run=F('variant_calls__analysis_run')
            ).distinct()

        def _parse_value(search_value):
            """
            Parse search value from DataTables request.
            If the value contains '_initial' prefix, it's parsed as JSON.

            Args:
                search_value (str): Search string from DataTables

            Returns:
                str: Parsed search value
            """
            if "_initial:" in search_value:
                return json.loads(search_value.split("_initial:")[1])
            return search_value

        def _is_initial_value(search_value):
            """
            Check if the search value contains initial filtering data.

            Args:
                search_value (str): Search string from DataTables

            Returns:
                bool: True if contains initial value, False otherwise
            """
            return "_initial:" in search_value and search_value.split("_initial:")[1] != "null"

        def get_kwarg_value(kwargs, key, default=None):
            """
            Extract value from kwargs, handling both single values and lists.
            """
            value = kwargs.get(key, default)
            if isinstance(value, (list, tuple)):
                try:
                    return value[0]
                except IndexError:
                    return default
            return value

        try:
            # Column mapping for ordering in different contexts
            ORDER_COLUMN_CHOICES = {
                "0": "id",
                "1": "patients",  # Changed to use annotated field
                "2": "areas",
                "3": "blocks",    # Changed to use annotated field
                "4": "sample_lib",
                "5": "sequencing_run",
                "6": "genes",     # Changed to use annotated field
                "7": "p_variant", # Changed to use p_variant annotation
                "8": "c_variants__nm_id",  # For aliases
            }

            # Extract DataTables parameters
            draw = int(kwargs.get('draw', None)[0])
            length = int(kwargs.get('length', None)[0])
            start = int(kwargs.get('start', None)[0])
            search_value = kwargs.get('search[value]', None)[0]
            order = kwargs.get('order[0][dir]', None)[0]
            order_column = kwargs.get('order[0][column]', None)[0]
            order_column = ORDER_COLUMN_CHOICES[order_column]

            # Extract filter parameters
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

            # Apply descending order if needed
            if order == 'desc':
                order_column = '-' + order_column

            # Get appropriate queryset based on context
            if model_block:
                queryset = _get_block_variants_queryset(block_id)
            elif model_area:
                queryset = _get_area_variants_queryset(area_id)
            else:
                queryset = _get_authorizated_queryset()

            total = queryset.count()

            # Apply filters based on parameters
            if sample_lib:
                queryset = queryset.filter(Q(variant_calls__sample_lib__id=sample_lib))

            if sequencing_run:
                queryset = queryset.filter(Q(variant_calls__sequencing_run__id=sequencing_run))

            if area:
                queryset = queryset.filter(
                    Q(variant_calls__sample_lib__na_sl_links__nucacid__area_na_links__area__id=area))

            if block:
                queryset = queryset.filter(
                    Q(variant_calls__sample_lib__na_sl_links__nucacid__area_na_links__area__block__id=block))

            if patient:
                queryset = queryset.filter(
                    Q(variant_calls__sample_lib__na_sl_links__nucacid__area_na_links__area__block__patient__id=patient))

            if coverage_value:
                queryset = queryset.filter(variant_calls__coverage=coverage_value)

            if log2r_value:
                queryset = queryset.filter(variant_calls__log2r=log2r_value)

            if ref_read_value:
                queryset = queryset.filter(variant_calls__ref_read=ref_read_value)

            if alt_read_value:
                queryset = queryset.filter(variant_calls__alt_read=alt_read_value)

            if variant:
                queryset = queryset.filter(
                    Q(c_variants__p_variants__name_meta__icontains=variant) |
                    Q(c_variants__c_var__icontains=variant)
                )

            if variant_file:
                queryset = queryset.filter(variant_calls__variant_file__name__icontains=variant_file)

            # Handle initial filtering from DataTables
            if is_initial:
                if search_value["model"] == "block":
                    queryset = queryset.filter(
                        variant_calls__sample_lib__na_sl_links__nucacid__area_na_links__area__block__id=int(search_value["id"]))

                if search_value["model"] == "area":
                    queryset = queryset.filter(
                        variant_calls__sample_lib__na_sl_links__nucacid__area_na_links__area__id=int(search_value["id"]))

            elif search_value:
                # General search across multiple fields
                queryset = queryset.filter(
                    Q(variant_calls__caller__icontains=search_value) |
                    Q(variant_calls__label__icontains=search_value) |
                    Q(variant_calls__coverage__icontains=search_value) |
                    Q(chrom__icontains=search_value) |
                    Q(ref__icontains=search_value) |
                    Q(alt__icontains=search_value) |
                    Q(avsnp150__icontains=search_value)
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

class VariantCall(models.Model):
    g_variant = models.ForeignKey(GVariant, on_delete=models.CASCADE, related_name="variant_calls")
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
    primary_site_counts = models.JSONField()

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

# MATERIALIZED VIEW: variants_view
#
# Description: It was created to access all variants more effectively according to the assets it is associated with.

"""
CREATE MATERIALIZED VIEW variants_view AS
SELECT DISTINCT ON (vc.id)
    ROW_NUMBER() OVER() AS id,
    vc.id AS variantcall_id,
    a.id AS area_id,
    a.name AS area_name,
    a.area_type,
    a.collection,
    b.id AS block_id,
    b.name AS block_name,
    sl.id AS samplelib_id,
    sl.name AS samplelib_name,
    g.id AS gene_id,
    g.name AS gene_name,
    g.chr AS chromosome,
    vc.coverage,
    vc.log2r,
    vc.caller,
    vc.ref_read,
    vc.alt_read,
    CASE 
        WHEN vc.ref_read > 0 THEN (vc.alt_read * 100.0) / (vc.ref_read + vc.alt_read)
        ELSE 0.0
    END AS vaf,
    vc.alias_meta as "alias",
    vc.variant_meta as "variant",
    gv.id AS gvariant_id,
    gv.chrom AS g_chromosome,
    gv.start AS g_start,
    gv.end AS g_end,
    gv.ref AS g_ref,
    gv.alt AS g_alt,
    gv.avsnp150,
    cv.id AS cvariant_id,
    cv.nm_id,
    cv.c_var,
    cv.exon,
    cv.func,
    pv.id AS pvariant_id,
    pv.reference_residues,
    pv.inserted_residues,
    pv.change_type,
    ar.id AS analysis_run_id,
    ar.name AS analysis_run_name,
	cgv.primary_site_counts as primary_site_counts
FROM 
    areas a
JOIN 
    block b ON a.block = b.id
JOIN 
    area_na_link anl ON anl.area_id = a.id
JOIN 
    nuc_acids na ON anl.nucacid_id = na.id
JOIN 
    na_sl_link nsl ON nsl.nucacid_id = na.id
JOIN 
    sample_lib sl ON nsl.sample_lib_id = sl.id
JOIN 
    variant_call vc ON vc.sample_lib_id = sl.id
JOIN 
    g_variant gv ON gv.id = vc.g_variant_id
JOIN 
    c_variant cv ON cv.g_variant_id = gv.id
JOIN 
    gene g ON cv.gene_id = g.id
JOIN 
    analysis_run ar ON vc.analysis_run_id = ar.id
LEFT JOIN 
    p_variant pv ON pv.c_variant_id = cv.id
JOIN 
    cosmic_hg38.cosmic_g_variant_view_with_id cgv on cgv.g_variant_id=gv.id
WHERE 
    a.area_type IS NOT NULL;
"""


# Here are some database indexes after need to create after to created the materialized view above
"""
CREATE UNIQUE INDEX ON variants_view (id);
CREATE INDEX idx_area_variants_area_id ON variants_view (area_id);
CREATE INDEX idx_area_variants_block_id ON variants_view (block_id);
"""

# Here are some helpfull commands
"""
drop materialized view variants_view;

select * from pg_catalog.pg_matviews;
"""

class CosmicGVariantView(models.Model):
    g_variant_id = models.IntegerField()
    chr = models.CharField(max_length=2)
    pos = models.IntegerField()
    ref = models.CharField(max_length=1)
    alt = models.CharField(max_length=1)
    gene_symbol = models.CharField(max_length=10)
    cosmic_aa = models.CharField(max_length=10)
    primary_site_counts = models.JSONField()
    primary_site_counts_merged = models.JSONField()
    primary_site_total = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'cosmic_g_variant_view_with_id_stats'

