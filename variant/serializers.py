from rest_framework import serializers
from .models import *
from sequencinglib.models import *
from areas.models import Areas
from blocks.models import Blocks

class VariantSerializer(serializers.ModelSerializer):
    DT_RowId = serializers.SerializerMethodField()
    patient = serializers.SerializerMethodField()
    block = serializers.SerializerMethodField()
    area = serializers.SerializerMethodField()
    gene = serializers.SerializerMethodField()
    p_variant = serializers.SerializerMethodField()
    c_variant = serializers.SerializerMethodField()
    g_variant = serializers.SerializerMethodField()
    sample_lib = serializers.SerializerMethodField()
    sequencing_run = serializers.SerializerMethodField()

    class Meta:
        model = VariantCall
        fields = ("id", "patient", "sample_lib", "sequencing_run", "block", "area", "gene", "p_variant", "c_variant", "g_variant", "DT_RowId",)

    def get_DT_RowId(self, obj):
       return getattr(obj, 'id')

    def get_patient(self,obj):
        block = Blocks.objects.filter(block_area_links__area__area_na_links__nucacid__na_sl_links__sample_lib=obj.sample_lib).first()
        return block.patient.name if block else ""

    def get_sample_lib(self,obj):
        return obj.sample_lib.name

    def get_sequencing_run(self,obj):
        return obj.sequencing_run.name

    def get_block(self,obj):
        block = Blocks.objects.filter(block_area_links__area__area_na_links__nucacid__na_sl_links__sample_lib=obj.sample_lib).first()
        return block.name if block else ""

    def get_area(self,obj):
        area = Areas.objects.filter(block__block_area_links__area__area_na_links__nucacid__na_sl_links__sample_lib=obj.sample_lib).first()
        return area.name if area else ""

    def get_p_variant(self,obj):
        try:
            p_variant = PVariant.objects.get(c_variant__g_variant__variant_call=obj)
            return f"p.{p_variant.change_type}-{p_variant.start}-{p_variant.end}" # TODO: format as expected
        except Exception as e:
            print(str(e))
            return None

    def get_c_variant(self,obj):
        try:
            c_variant = CVariant.objects.get(g_variant__variant_call=obj)
            return f"{c_variant.c_var}" # TODO: format as expected
        except Exception as e:
            print(str(e))
            return None

    def get_g_variant(self,obj):
        try:
            g_variant = GVariant.objects.get(variant_call=obj)
            return f"{g_variant.chrom}-{g_variant.start}-{g_variant.end}-{g_variant.avsnp150}" # TODO: format as expected
        except Exception as e:
            print(str(e))
            return None

    def get_gene(self,obj):
        try:
            return CVariant.objects.get(g_variant__variant_call=obj).gene.name
        except Exception as e:
            return None
