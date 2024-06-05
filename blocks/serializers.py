from rest_framework import serializers
from .models import *
from lab.models import Patients

class BlocksSerializer(serializers.ModelSerializer):
    num_areas = serializers.IntegerField()
    patient_id = serializers.SerializerMethodField()
    DT_RowId = serializers.SerializerMethodField()
    project_id = serializers.SerializerMethodField()
    body_site = serializers.SerializerMethodField()
    block_url = serializers.SerializerMethodField()
    patient = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()

    class Meta:
        model = Blocks
        fields = ("bl_id","name","project_id","patient_id","project","patient",
                  "diagnosis","body_site","thickness","date_added","num_areas",
                  "DT_RowId","block_url","scan_number")

    def get_DT_RowId(self, obj):
           return getattr(obj, 'bl_id')

    def get_project(self, obj):
        return obj.project.name if obj.project else None

    def get_patient(self, obj):
        return obj.patient.pat_id if obj.patient else None

    def get_body_site(self,obj):
        return obj.body_site.name if obj.body_site else None

    def get_patient_id(self,obj):
        return obj.patient.pa_id if obj.patient else None

    # def get_patient_name(self,obj):
    #     return obj.patient.pat_id if obj.patient else None

    def get_project_id(self,obj):
        return obj.project.pr_id if obj.project else None

    # def get_project_name(self,obj):
    #     return obj.project.name if obj.project else None

    # def get_collection_label(self,obj):
    #     return obj.get_collection_display()

    def get_block_url(self,obj):
        return obj.get_block_url()

class SingleBlockSerializer(serializers.ModelSerializer):
    patient = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()

    class Meta:
        model = Blocks
        fields = "__all__"

    def get_patient(self,obj):
        return obj.patient.pat_id

    def get_project(self,obj):
        return obj.project.name
