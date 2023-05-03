from rest_framework import serializers
from .models import *
from lab.models import Patients

class BlocksSerializer(serializers.ModelSerializer):
    num_areas = serializers.IntegerField()
    patient_id = serializers.SerializerMethodField()
    patient_name = serializers.SerializerMethodField()
    DT_RowId = serializers.SerializerMethodField()
    project_id = serializers.SerializerMethodField()
    project_name = serializers.SerializerMethodField()
    body_site = serializers.SerializerMethodField()
    collection_label = serializers.SerializerMethodField()

    class Meta:
        model = Blocks
        fields = ("bl_id","name","project_id","project_name","patient_id","patient_name","diagnosis","body_site","thickness","collection","collection_label","date_added","num_areas","DT_RowId",)

    def get_value(self,obj):
        return obj.patient.pat_id

    def get_DT_RowId(self, obj):
           return getattr(obj, 'bl_id')

    def get_project(self, obj):
        return obj.project.name

    def get_body_site(self,obj):
        return obj.body_site.name if obj.body_site else None

    def get_patient_id(self,obj):
        return obj.patient.pa_id if obj.patient else None

    def get_patient_name(self,obj):
        return obj.patient.pat_id if obj.patient else None

    def get_project_id(self,obj):
        return obj.project.pr_id if obj.project else None

    def get_project_name(self,obj):
        return obj.project.name if obj.project else None

    def get_collection_label(self,obj):
        return obj.get_collection_display()
