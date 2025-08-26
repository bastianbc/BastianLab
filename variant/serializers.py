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
    areas = serializers.SerializerMethodField()
    blocks = serializers.SerializerMethodField()
    genes = serializers.SerializerMethodField()
    sample_libs = serializers.SerializerMethodField()
    sequencing_runs = serializers.SerializerMethodField()
    cosmic_gene_symbol = serializers.SerializerMethodField()
    cosmic_aa = serializers.SerializerMethodField()
    cosmic_primary_site_counts = serializers.SerializerMethodField()
    total_calls = serializers.SerializerMethodField()

    class Meta:
        model = GVariant
        fields = ("id", "chrom", "start", "ref", "alt", "patients", "areas",
                  "blocks", "sample_libs", "sequencing_runs", "genes", "cosmic_gene_symbol",
                  "cosmic_aa", "cosmic_primary_site_counts", "total_calls", "DT_RowId", )

    def get_DT_RowId(self, obj):
        """DataTables row ID for frontend identification."""
        return getattr(obj, 'id')

    def _get_unique_objects(self, objects):
        """Helper method to get unique objects by id"""
        if not objects:
            return []

        unique_dict = {}
        for obj in objects:
            if obj and 'id' in obj:
                unique_dict[obj['id']] = obj

        return list(unique_dict.values())

    def get_patients(self, obj):
        patients = getattr(obj, 'patients', [])
        return self._get_unique_objects(patients)

    def get_areas(self, obj):
        areas = getattr(obj, 'areas', [])
        return self._get_unique_objects(areas)

    def get_blocks(self, obj):
        blocks = getattr(obj, 'blocks', [])
        return self._get_unique_objects(blocks)

    def get_genes(self, obj):
        genes = getattr(obj, 'genes', [])
        return self._get_unique_objects(genes)

    def get_sample_libs(self, obj):
        sample_libs = getattr(obj, 'sample_libs', [])
        return self._get_unique_objects(sample_libs)

    def get_sequencing_runs(self, obj):
        sequencing_runs = getattr(obj, 'sequencing_runs', [])
        return self._get_unique_objects(sequencing_runs)

    def get_cosmic_gene_symbol(self, obj):
        return getattr(obj, 'gene_symbol', None)

    def get_cosmic_aa(self, obj):
        return getattr(obj, 'cosmic_aa', None)

    def get_cosmic_primary_site_counts(self, obj):
        data = getattr(obj, 'primary_site_counts', None)
        total = sum(data.values()) if data else 0
        return total

    def get_total_calls(self, obj):
        return obj.variant_calls.count()

class VariantsViewSerializer(serializers.ModelSerializer):
    DT_RowId = serializers.SerializerMethodField()

    class Meta:
        model = VariantsView
        fields = ("analysis_run_name","gene_name","pvariant_id","alias","coverage","vaf","DT_RowId",)
