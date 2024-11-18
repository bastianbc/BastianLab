from rest_framework import serializers
from .models import *
from sequencinglib.models import *
from areas.models import Areas
from blocks.models import Blocks

class VariantSerializer(serializers.ModelSerializer):
    block = serializers.SerializerMethodField()
    area = serializers.SerializerMethodField()
    ref = serializers.SerializerMethodField()
    pos = serializers.SerializerMethodField()
    alt = serializers.SerializerMethodField()
    gene = serializers.SerializerMethodField()
    sample_lib = serializers.SerializerMethodField()

    class Meta:
        model = VariantCall
        fields = ("id", "sample_lib", "sequencing_run", "block", "area", "ref", "pos", "alt", "gene",)

    def get_block(self,obj):
        return Blocks.objects.filter(block_area_links__area__area_na_links__nucacid__na_sl_links__sample_lib=obj.sample_lib).first()

    def get_area(self,obj):
        return Areas.objects.filter(block__block_area_links__area__area_na_links__nucacid__na_sl_links__sample_lib=obj.sample_lib).first()

    def get_ref(self,obj):
        try:
            return PVariant.objects.get(c_variant__g_variant__variant_call=obj).ref
        except Exception as e:
            return None

    def get_pos(self,obj):
        try:
            return PVariant.objects.get(c_variant__g_variant__variant_call=obj).pos
        except Exception as e:
            return None

    def get_alt(self,obj):
        try:
            return PVariant.objects.get(c_variant__g_variant__variant_call=obj).alt
        except Exception as e:
            return None

    def get_gene(self,obj):
        try:
            return CVariant.objects.get(g_variant__variant_call=obj).gene
        except Exception as e:
            return None

    def get_sample_lib(self,obj):
        return obj.sample_lib.name
