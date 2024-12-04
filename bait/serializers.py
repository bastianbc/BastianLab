from rest_framework import serializers
from .models import *

class BaitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bait
        fields = "__all__"
