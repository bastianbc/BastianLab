from rest_framework import serializers
from .models import *
from lab.models import Patients

class BlocksSerializer(serializers.ModelSerializer):
    num_areas = serializers.IntegerField()
    patient = serializers.StringRelatedField()

    class Meta:
        model = Blocks
        fields = ("bl_id","patient","diagnosis","body_site","gross","num_areas",)

    def get_value(self,obj):
        return obj.patient.pat_id
