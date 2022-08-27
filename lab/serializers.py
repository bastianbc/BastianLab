from rest_framework import serializers
from .models import *

class PatientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patients
        fields = ("pat_id","source","sex","race","project",)
