from rest_framework import serializers
from .models import *
from sequencinglib.models import *
from sequencinglib.serializers import SingleSequencingLibSerializer

class SequencingRunSerializer(serializers.ModelSerializer):
    DT_RowId = serializers.SerializerMethodField()
    facility_label = serializers.SerializerMethodField()
    sequencer_label = serializers.SerializerMethodField()
    pe_label = serializers.SerializerMethodField()
    num_sequencinglibs = serializers.IntegerField()
    num_file_sets = serializers.IntegerField()


    class Meta:
        model = SequencingRun
        fields = ("id", "name", "date", "facility", "facility_label", "sequencer", "sequencer_label", "pe",
                  "pe_label", "amp_cycles", "date_run", "num_sequencinglibs", "DT_RowId", "num_file_sets")

    def get_DT_RowId(self, obj):
       return getattr(obj, 'id')

    def get_facility_label(self,obj):
        return obj.get_facility_display()

    def get_sequencer_label(self,obj):
        return obj.get_sequencer_display()

    def get_pe_label(self,obj):
        return obj.get_pe_display()

class UsedSequencingLibSerializer(serializers.ModelSerializer):
    buffer = serializers.SerializerMethodField()

    class Meta:
        model = SequencingLib
        fields = ("id", "name", "date", "nmol", "buffer",)

    def get_buffer(self,obj):
        return obj.get_buffer_display()

class SingleSequencingRunSerializer(serializers.ModelSerializer):
    sequencing_libs = SingleSequencingLibSerializer(many=True)

    class Meta:
        model = SequencingRun
        fields = "__all__"
