from rest_framework import serializers
from .models import *
from lab.models import Patients

class BlocksSerializer(serializers.ModelSerializer):
    num_areas = serializers.IntegerField()
    patient = serializers.StringRelatedField()
    DT_RowId = serializers.SerializerMethodField()
    project = serializers.StringRelatedField()
    body_site = serializers.SerializerMethodField()
    collection_label = serializers.SerializerMethodField()

    class Meta:
        model = Blocks
        fields = ("bl_id","name","project","patient","diagnosis","body_site","thickness","collection","collection_label","date_added","num_areas","DT_RowId",)

    def get_value(self,obj):
        return obj.patient.pat_id

    def get_DT_RowId(self, obj):
           return getattr(obj, 'bl_id')

    def get_project(self, obj):
        return obj.project.name

    def get_body_site(self,obj):
        return obj.body_site.name if obj.body_site else None

    def get_collection_label(self,obj):
        return obj.get_collection_display()
