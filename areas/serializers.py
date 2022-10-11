from rest_framework import serializers
from .models import *
from lab.models import Patients

class AreasSerializer(serializers.ModelSerializer):
    num_nucacids = serializers.IntegerField()
    DT_RowId = serializers.SerializerMethodField()
    block = serializers.StringRelatedField()
    project = serializers.StringRelatedField()

    class Meta:
        model = Areas
        fields = ("ar_id", "name", "area", "block", "project", "collection", "area_type", "he_image", "completion_date", "investigator","num_nucacids", "DT_RowId",)

    def get_DT_RowId(self, obj):
        return getattr(obj, 'ar_id')

    def get_block(self,obj):
        return obj.block.name

    def get_project(self, obj):
        return obj.project.name
