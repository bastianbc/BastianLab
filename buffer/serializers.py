from rest_framework import serializers
from .models import *

class BufferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Buffer
        fields = "__all__"
