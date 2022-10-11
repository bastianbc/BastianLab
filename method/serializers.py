from rest_framework import serializers
from .models import *

class MethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Method
        fields = "__all__"
