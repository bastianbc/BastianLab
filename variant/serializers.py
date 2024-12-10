from rest_framework import serializers
from .models import *
from sequencinglib.models import *
from areas.models import Areas
from blocks.models import Blocks

class VariantSerializer(serializers.ModelSerializer):
    DT_RowId = serializers.SerializerMethodField()
    patients = serializers.CharField(read_only=True)
    blocks = serializers.CharField(read_only=True)
    areas = serializers.CharField(read_only=True)
    genes = serializers.CharField(read_only=True)
    cvariant = serializers.CharField(read_only=True)
    pvariant = serializers.CharField(read_only=True)
    gvariant = serializers.CharField(read_only=True)
    sample_lib = serializers.SerializerMethodField()
    sequencing_run = serializers.SerializerMethodField()

    class Meta:
        model = VariantCall
        fields = ("id", "patients", "sample_lib", "sequencing_run", "blocks", "areas", "genes", "pvariant",
        "gvariant", "DT_RowId", 'cvariant')

    def get_DT_RowId(self, obj):
       return getattr(obj, 'id')

    def get_sample_lib(self,obj):
        return obj.sample_lib.name

    def get_sequencing_run(self,obj):
        return obj.sequencing_run.name

    # def get_p_variant(self,obj):
    #     try:
    #         p_variant = PVariant.objects.filter(c_variant__g_variant__variant_call=obj).first()
    #         return f"{p_variant.name_meta}" # TODO: format as expected
    #     except Exception as e:
    #         print(str(e))
    #         return None

    # def get_c_variant(self,obj):
    #     try:
    #         c_variant = CVariant.objects.filter(g_variant__variant_call=obj).first()
    #         return f"{c_variant.c_var}" # TODO: format as expected
    #     except Exception as e:
    #         print(str(e))
    #         return None

    # def get_g_variant(self,obj):
    #     try:
    #         g_variant = GVariant.objects.get(variant_call=obj)
    #         return f"{g_variant.chrom}-{g_variant.start}-{g_variant.end}-{g_variant.avsnp150}" # TODO: format as expected
    #     except Exception as e:
    #         print(str(e))
    #         return None

    def get_gene(self,obj):
        try:
            return CVariant.objects.get(g_variant__variant_call=obj).gene.name
        except Exception as e:
            return None
