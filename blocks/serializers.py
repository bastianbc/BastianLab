from rest_framework import serializers
from .models import *

class BlocksSerializer(serializers.ModelSerializer):
    num_areas = serializers.IntegerField()

    class Meta:
        model = Blocks
        fields = ("bl_id","patient","diagnosis","body_site","gross","num_areas",)
