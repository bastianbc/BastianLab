from rest_framework import serializers
from .models import *
from sequencinglib.models import *

class SequencingRunSerializer(serializers.ModelSerializer):
    DT_RowId = serializers.SerializerMethodField()
    facility = serializers.SerializerMethodField()
    sequencer = serializers.SerializerMethodField()
    pe = serializers.SerializerMethodField()

    class Meta:
        model = SequencingRun
        fields = ("id", "name", "date", "facility", "sequencer", "pe", "amp_cycles", "date_run", "DT_RowId",)

    def get_DT_RowId(self, obj):
       return getattr(obj, 'id')

    def get_facility(self,obj):
        return obj.get_facility_display()

    def get_sequencer(self,obj):
        return obj.get_sequencer_display()

    def get_pe(self,obj):
        return obj.get_pe_display()

class UsedSequencingLibSerializer(serializers.ModelSerializer):
    buffer = serializers.SerializerMethodField()

    class Meta:
        model = SequencingLib
        fields = ("id", "name", "date", "nmol", "buffer",)

    def get_buffer(self,obj):
        return obj.get_buffer_display()
