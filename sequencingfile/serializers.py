from rest_framework import serializers
from .models import *
from sequencinglib.models import *

class SequencingFileSerializer(serializers.ModelSerializer):
    # DT_RowId = serializers.SerializerMethodField()
    sequencing_file_set = serializers.SerializerMethodField()
    path = serializers.SerializerMethodField()

    class Meta:
        model = SequencingFile
        fields = ("file_id", "name", "checksum", "sequencing_file_set", "path")

    # def get_DT_RowId(self, obj):
    #    return getattr(obj, 'id')
    #
    def get_sequencing_file_set(self,obj):
        if obj.sequencing_file_set:
            return obj.sequencing_file_set.prefix
        else:
            return

    def get_path(self,obj):
        if obj.sequencing_file_set:
            return obj.sequencing_file_set.path
        else:
            return

class SequencingFileSetSerializer(serializers.ModelSerializer):
    num_sequencing_files = serializers.IntegerField()
    DT_RowId = serializers.SerializerMethodField()
    sample_lib = serializers.SerializerMethodField()
    sequencing_run = serializers.SerializerMethodField()

    class Meta:
        model = SequencingFileSet
        fields = ("set_id","DT_RowId", "sample_lib", "sequencing_run", "prefix", "path", "num_sequencing_files", "date_added")

    def get_DT_RowId(self, obj):
       return getattr(obj, 'set_id')

    def get_sample_lib(self,obj):
        return obj.sample_lib.name if obj.sample_lib else None

    def get_sequencing_run(self,obj):
        return obj.sequencing_run.name if obj.sequencing_run else None
