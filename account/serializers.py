from rest_framework import serializers
from .models import *

class AccountSerializer(serializers.ModelSerializer):
    group = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id","username","first_name","last_name","group","last_login",)

    def get_group(self,obj):
        if obj.groups:
            return obj.groups.first().name
        return ""
