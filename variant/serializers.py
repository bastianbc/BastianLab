from rest_framework import serializers
from .models import *
from sequencinglib.models import *

class VariantSerializer(serializers.ModelSerializer):
    block = serializers.SerializerMethodField()
    area = serializers.SerializerMethodField()
    ref = serializers.SerializerMethodField()
    pos = serializers.SerializerMethodField()
    alt = serializers.SerializerMethodField()

    class Meta:
        model = VariantCall
        fields = ("id", "sample_lib", "sequencing_run", "block", "area", "Ref", "Pos", "Alt", "Gene",)

    def get_block(self,obj):
        return ""

    def get_area(self,obj):
        return ""

    def get_ref(self,obj):
        return ""

    def get_pos(self,obj):
        return ""

    def get_alt(self,obj):
        return ""
