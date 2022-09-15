from rest_framework import serializers
from .models import *
from lab.models import Patients

class AreasSerializer(serializers.ModelSerializer):
    num_nucacids = serializers.IntegerField()
    DT_RowId = serializers.SerializerMethodField()

    class Meta:
        model = Areas
        fields = ("old_area_id", "area", "old_block_id", "collection", "area_type", "he_image", "na_id", "completion_date", "investigator", "image", "notes", "project", "block", "ar_id", "num_nucacids", "DT_RowId",)

    def get_DT_RowId(self, obj):
        return getattr(obj, 'ar_id')
