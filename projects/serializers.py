from rest_framework import serializers
from .models import *

class ProjectsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projects
        fields = ("abbreviation","name","pi","date_start","speedtype","pr_id",)
