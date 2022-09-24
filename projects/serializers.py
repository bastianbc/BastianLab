from rest_framework import serializers
from .models import *

class ProjectsSerializer(serializers.ModelSerializer):
    DT_RowId = serializers.SerializerMethodField()
    num_blocks = serializers.IntegerField()

    class Meta:
        model = Projects
        fields = ("abbreviation","name","pi","date_start","speedtype","pr_id","num_blocks","DT_RowId",)

    def get_DT_RowId(self, obj):
        return getattr(obj, 'pr_id')
