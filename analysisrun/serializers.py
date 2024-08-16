from rest_framework import serializers
from .models import *

class AnalysisRunSerializer(serializers.ModelSerializer):
    DT_RowId = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = AnalysisRun
        fields = ("id", "name", "pipeline", "genome", "date", "sheet", "status", "DT_RowId", )

    def get_DT_RowId(self, obj):
       return getattr(obj, 'id')

    def get_status(self, obj):
        return obj.get_status_display()
