from rest_framework import serializers
from .models import *
from sequencinglib.models import *

class SequencingFileSerializer(serializers.ModelSerializer):
    DT_RowId = serializers.SerializerMethodField()

    class Meta:
        model = SequencingFile
        fields = ("id", "sample_lib", "folder_name", "read1_file", "read1_checksum", "read1_count", "read2_file", "read2_checksum", "read2_count", "is_read_count_equal", "path", "DT_RowId",)

    def get_DT_RowId(self, obj):
       return getattr(obj, 'id')
