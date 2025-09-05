from rest_framework import serializers
from .models import *
from lab.models import Patient

class BlocksSerializer(serializers.ModelSerializer):
    num_areas = serializers.IntegerField()
    num_variants = serializers.CharField()
    patient_id = serializers.SerializerMethodField()
    DT_RowId = serializers.SerializerMethodField()
    body_site = serializers.SerializerMethodField()
    block_url = serializers.SerializerMethodField()
    patient = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()

    class Meta:
        model = Block
        fields = ("id","name","patient_id","project","patient","diagnosis","body_site","thickness",
                  "date_added","num_areas","DT_RowId","block_url","scan_number","num_variants")

    def get_DT_RowId(self, obj):
        return getattr(obj, 'id')

    def get_project(self, obj):
        # prefetch_related('block_projects') will make this O(1) per row
        return ", ".join([p.abbreviation for p in obj.block_projects.all()])

    def get_patient(self, obj):
        # select_related('patient') -> O(1)
        return obj.patient.pat_id if obj.patient else None

    def get_body_site(self, obj):
        # select_related('body_site') -> O(1)
        return obj.body_site.name if obj.body_site else None

    def get_patient_id(self, obj):
        return obj.patient.id if obj.patient else None

    def get_block_url(self, obj):
        # single value from context (no per-row query)
        return self.context.get("block_url")

class SingleBlockSerializer(serializers.ModelSerializer):
    patient = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()

    class Meta:
        model = Block
        fields = "__all__"

    def get_patient(self,obj):
        return obj.patient.pat_id if obj.patient else None

    def get_project(self,obj):
        return ", ".join([p.name for p in obj.block_projects.all()])
