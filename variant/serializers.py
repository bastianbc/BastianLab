from rest_framework import serializers
from .models import *
from sequencinglib.models import *
from areas.models import Area

class VariantSerializer(serializers.ModelSerializer):
    DT_RowId = serializers.SerializerMethodField()
    patients = serializers.CharField(read_only=True)
    blocks = serializers.CharField(read_only=True)
    areas = serializers.CharField(read_only=True)
    genes = serializers.CharField(read_only=True)
    variant_meta = serializers.CharField(read_only=True)
    alias_meta = serializers.CharField(read_only=True)
    sample_lib = serializers.SerializerMethodField()
    sequencing_run = serializers.SerializerMethodField()

    class Meta:
        model = VariantCall
        fields = ("id", "patients", "areas", "variant_meta", "alias_meta", "blocks", "sample_lib",
                  "sequencing_run", "genes", "DT_RowId", )

    def get_DT_RowId(self, obj):
       return getattr(obj, 'id')

    def get_sample_lib(self,obj):
        return obj.sample_lib.name

    def get_sequencing_run(self,obj):
        return obj.sequencing_run.name


class VariantSerializerBlockArea(serializers.ModelSerializer):
    DT_RowId = serializers.SerializerMethodField()
    blocks = serializers.CharField(read_only=True)
    areas = serializers.CharField(read_only=True)
    genes = serializers.CharField(read_only=True)
    sample_lib = serializers.SerializerMethodField()
    vaf = serializers.FloatField()
    p_variant = serializers.CharField(read_only=True)

    class Meta:
        model = VariantCall
        fields = ("id", "areas", "sample_lib", "genes", "DT_RowId", "coverage", "vaf", "analysis_run", "blocks",  "p_variant")

    def get_DT_RowId(self, obj):
       return getattr(obj, 'id')

    def get_sample_lib(self,obj):
        return obj.sample_lib.name

class VariantsViewSerializer(serializers.ModelSerializer):
    DT_RowId = serializers.SerializerMethodField()

    class Meta:
        model = VariantsView
        fields = ("analysis_run_name","gene_name","pvariant_id","alias","coverage","vaf","DT_RowId",)
