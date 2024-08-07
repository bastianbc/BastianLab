from rest_framework import serializers
from .models import *

class AnalysisRunSerializer(serializers.ModelSerializer):
    DT_RowId = serializers.SerializerMethodField()

    class Meta:
        model = AnalysisRun
        fields = ("id", "pipeline", "genome", "date", "sheet", "DT_RowId", )

    def get_DT_RowId(self, obj):
       return getattr(obj, 'id')
