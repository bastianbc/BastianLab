from rest_framework import serializers
from .models import *
import os

class SampleQCSerializer(serializers.ModelSerializer):
    DT_RowId = serializers.SerializerMethodField()
    sample_lib = serializers.SerializerMethodField()
    sequencing_run = serializers.SerializerMethodField()
    analysis_run = serializers.SerializerMethodField()
    insert_size_histogram = serializers.SerializerMethodField()

    class Meta:
        model = SampleQC
        fields = ("id","sample_lib","sequencing_run","analysis_run","insert_size_histogram","DT_RowId")

    def get_sequencing_run(self,obj):
        return obj.sequencing_run.name

    def get_sample_lib(self,obj):
        return obj.sample_lib.name

    def get_analysis_run(self,obj):
        return obj.analysis_run.name

    def get_DT_RowId(self, obj):
        return getattr(obj, 'id')

    def get_insert_size_histogram(self, obj):
        return os.path.join(obj.variant_file.directory, obj.insert_size_histogram)
