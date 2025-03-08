from rest_framework import serializers
from .models import *

class SampleQCSerializer(serializers.ModelSerializer):
    class Meta:
        model = SampleQC
        fields = ("id","sample_lib","sequencing_run","analysis_run","insert_size_histogram","DT_RowId")

    def get_sequencing_run_name(self,obj):
        return obj.sequencing_run.name

    def get_sample_lib_name(self,obj):
        return obj.sample_lib.name

    def get_analysis_run_name(self,obj):
        return obj.analysis_run.name
