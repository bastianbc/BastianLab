from rest_framework import serializers
from .models import *

class PatientsSerializer(serializers.ModelSerializer):
    num_blocks = serializers.IntegerField()

    class Meta:
        model = Patients
        fields = ("pat_id","source","sex","race","project","num_blocks",)
