from rest_framework import serializers
from .models import *
from sequencinglib.models import *

class GeneSerializer(serializers.ModelSerializer):

    class Meta:
        model = Gene
        fields = ("id", "name", "chr", "start", "end", "hg",)
