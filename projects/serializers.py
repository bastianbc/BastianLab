from rest_framework import serializers
from .models import *

class ProjectsSerializer(serializers.ModelSerializer):
    DT_RowId = serializers.SerializerMethodField()

    class Meta:
        model = Projects
        fields = ("abbreviation","name","pi","date_start","speedtype","pr_id","DT_RowId",)

    def get_DT_RowId(self, obj):
        return getattr(obj, 'pr_id')
