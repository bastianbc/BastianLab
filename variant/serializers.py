from rest_framework import serializers
from .models import *
from sequencinglib.models import *
from areas.models import Area
from collections import defaultdict


class GVariantSerializer(serializers.ModelSerializer):
    """
    Serializer for GVariant model with annotated fields from the query_by_args method.
    This serializer handles the data structure returned by GVariant.query_by_args().
    Handles multiple variant calls by aggregating values with comma separation.
    """
    DT_RowId = serializers.SerializerMethodField()
    patients = serializers.SerializerMethodField()
    blocks = serializers.SerializerMethodField()
    areas = serializers.SerializerMethodField()
    genes = serializers.SerializerMethodField()
    sample_lib = serializers.SerializerMethodField()
    sequencing_run = serializers.SerializerMethodField()
    gene_symbol = serializers.SerializerMethodField()
    cosmic_aa = serializers.SerializerMethodField()
    primary_site_counts = serializers.SerializerMethodField()
    primary_site_count_detail = serializers.SerializerMethodField()
    total_calls = serializers.SerializerMethodField()

    class Meta:
        model = GVariant
        fields = ("id", "chrom", "start", "ref", "alt", "patients", "areas",
                  "blocks", "sample_lib", "sequencing_run", "genes", "gene_symbol",
                  "cosmic_aa", "primary_site_counts", "total_calls", "DT_RowId", "primary_site_count_detail", )

    def get_DT_RowId(self, obj):
        """DataTables row ID for frontend identification."""
        return getattr(obj, 'id')

    def get_patients(self, obj):
        """Get list of unique patient (id, name) tuples."""
        patients = obj.variant_calls.filter(
            sample_lib__na_sl_links__nucacid__area_na_links__area__block__patient__isnull=False
        ).values_list(
            'sample_lib__na_sl_links__nucacid__area_na_links__area__block__patient__id',
            'sample_lib__na_sl_links__nucacid__area_na_links__area__block__patient__pat_id',
        ).distinct()

        # Convert to list of tuples (id, name)
        return list(patients) if patients else []

    def get_blocks(self, obj):
        """Get list of unique block (id, name) tuples."""
        blocks = obj.variant_calls.filter(
            sample_lib__na_sl_links__nucacid__area_na_links__area__block__isnull=False
        ).values_list(
            'sample_lib__na_sl_links__nucacid__area_na_links__area__block__id',
            'sample_lib__na_sl_links__nucacid__area_na_links__area__block__name',
        ).distinct()

        # Convert to list of tuples (id, name)
        return list(blocks) if blocks else []

    def get_areas(self, obj):
        """Get list of unique area (id, name) tuples."""
        areas = obj.variant_calls.filter(
            sample_lib__na_sl_links__nucacid__area_na_links__area__isnull=False
        ).values_list(
            'sample_lib__na_sl_links__nucacid__area_na_links__area__id',
            'sample_lib__na_sl_links__nucacid__area_na_links__area__name',
        ).distinct()

        # Convert to list of tuples (id, name)
        return list(areas) if areas else []

    def get_genes(self, obj):
        """Get list of unique gene (id, name) tuples."""
        # Get unique genes from c variants with both id and name
        genes_data = []
        seen_ids = set()

        for cv in obj.c_variants.all():
            if cv.gene and cv.gene.id not in seen_ids:
                genes_data.append((cv.gene.id, cv.gene.name))
                seen_ids.add(cv.gene.id)

        return genes_data if genes_data else []

    def get_sample_lib(self, obj):
        """Get list of unique sample library (id, name) tuples."""
        # Get unique sample libraries with both id and name
        sample_libs_data = []
        seen_ids = set()

        for vc in obj.variant_calls.all():
            if vc.sample_lib and vc.sample_lib.id not in seen_ids:
                sample_libs_data.append((vc.sample_lib.id, vc.sample_lib.name))
                seen_ids.add(vc.sample_lib.id)

        return sample_libs_data if sample_libs_data else []

    def get_sequencing_run(self, obj):
        """Get list of unique sequencing run (id, name) tuples."""
        # Get unique sequencing runs with both id and name
        seq_runs_data = []
        seen_ids = set()

        for vc in obj.variant_calls.all():
            if vc.sequencing_run and vc.sequencing_run.id not in seen_ids:
                seq_runs_data.append((vc.sequencing_run.id, vc.sequencing_run.name))
                seen_ids.add(vc.sequencing_run.id)

        return seq_runs_data if seq_runs_data else []

    def get_total_calls(self, obj):
        return obj.variant_calls.count()

    def get_gene_symbol(self, obj):
        try:
            cgv = CosmicGVariantView.objects.get(g_variant_id=obj.id)
            return cgv.gene_symbol
        except Exception as e:
            return None

    def get_cosmic_aa(self, obj):
        try:
            cgv = CosmicGVariantView.objects.get(g_variant_id=obj.id)
            return cgv.cosmic_aa
        except Exception as e:
            return None

    def get_primary_site_counts(self, obj):
        print("*"*30)
        try:
            qs = CosmicGVariantView.objects.filter(g_variant_id=obj.id).values_list("primary_site_counts", flat=True)
            if not qs:
                return None
            merged = defaultdict(int)
            for record in qs:
                if not record:
                    continue
                for site, count in record.items():
                    merged[site] += int(count) if count is not None else 0

            total = sum(merged.values())
            print(total)
            return total
        except Exception as e:
            print(e)
            return None

    def get_primary_site_count_detail(self, obj):
        try:
            qs = CosmicGVariantView.objects.filter(g_variant_id=obj.id).values_list("primary_site_counts", flat=True)

            merged = defaultdict(int)
            for record in qs:
                if not record:
                    continue
                for site, count in record.items():
                    merged[site] += int(count) if count is not None else 0
            print(merged)
            print(type(merged))
            return str(dict(merged))
        except Exception as e:
            print(e)
            return None

class VariantsViewSerializer(serializers.ModelSerializer):
    DT_RowId = serializers.SerializerMethodField()

    class Meta:
        model = VariantsView
        fields = ("analysis_run_name","gene_name","pvariant_id","alias","coverage","vaf","DT_RowId",)
