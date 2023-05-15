from rest_framework import serializers
from .models import *
from sequencinglib.models import *

class VariantSerializer(serializers.ModelSerializer):
    block = serializers.SerializerMethodField()
    area = serializers.SerializerMethodField()
    ref = serializers.SerializerMethodField()
    pos = serializers.SerializerMethodField()
    alt = serializers.SerializerMethodField()
    gene = serializers.SerializerMethodField()

    class Meta:
        model = VariantCall
        fields = ("id", "sample_lib", "sequencing_run", "block", "area", "ref", "pos", "alt", "gene",)

    def get_block(self,obj):
        return ""

    def get_area(self,obj):
        return ""

    def get_ref(self,obj):
        if obj.g_variant:
            if obj.g_variant.c_variants.first():
                if obj.g_variant.c_variants.first().p_variants.first():
                    return obj.g_variant.c_variants.first().p_variants.first().ref
        return None

    def get_pos(self,obj):
        if obj.g_variant:
            if obj.g_variant.c_variants.first():
                if obj.g_variant.c_variants.first().p_variants.first():
                    return obj.g_variant.c_variants.first().p_variants.first().pos
        return None

    def get_alt(self,obj):
        if obj.g_variant:
            if obj.g_variant.c_variants.first():
                if obj.g_variant.c_variants.first().p_variants.first():
                    return obj.g_variant.c_variants.first().p_variants.first().alt
        return None

    def get_gene(self,obj):
        return ""
