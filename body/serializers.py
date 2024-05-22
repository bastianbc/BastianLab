from rest_framework import serializers
from .models import *

class BodySerializer(serializers.ModelSerializer):
    class Meta:
        model = Body
        fields = "__all__"
