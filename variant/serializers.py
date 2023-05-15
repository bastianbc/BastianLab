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
        return ""
