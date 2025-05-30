from rest_framework import serializers
from .models import *
from lab.models import Patient

class AreasSerializer(serializers.ModelSerializer):
    num_nucacids = serializers.IntegerField()
    num_variants = serializers.IntegerField()
    DT_RowId = serializers.SerializerMethodField()
    num_blocks = serializers.IntegerField()
    num_projects = serializers.IntegerField()
    investigator = serializers.SerializerMethodField()
    num_samplelibs = serializers.IntegerField()
    completion_date = serializers.SerializerMethodField()
    area_type_label = serializers.SerializerMethodField()

    class Meta:
        model = Area
        fields = ("id", "name", "num_blocks", "num_projects", "area_type", "area_type_label", "completion_date",
                  "investigator", "num_nucacids", "num_samplelibs", "DT_RowId", "num_variants",)

    def get_DT_RowId(self, obj):
        return getattr(obj, 'id')

    def get_investigator(self, obj):
        return ", ".join([p.pi for p in obj.block.block_projects.all()])

    def get_block_name(self,obj):
        return obj.block.name if obj.block else None

    def get_block_id(self,obj):
        return obj.block.id if obj.block else None

    def get_project_id(self,obj):
        return obj.block.project.pr_id if obj.block.project else None

    def get_project_name(self,obj):
        return obj.block.project.name if obj.block.project else None

    def get_completion_date(self,obj):
        return ""

    def get_area_type_label(self,obj):
        return obj.area_type.name if obj.area_type else None
