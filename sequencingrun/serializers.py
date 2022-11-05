from rest_framework import serializers
from .models import *

class SequencingRunSerializer(serializers.ModelSerializer):
    DT_RowId = serializers.SerializerMethodField()
    facility = serializers.SerializerMethodField()
    sequencer = serializers.SerializerMethodField()

    class Meta:
        model = SequencingRun
        fields = ("id", "name", "date", "facility", "sequencer", "date_run", "DT_RowId",)

    def get_DT_RowId(self, obj):
       return getattr(obj, 'id')

    def get_facility(self,obj):
        return obj.get_facility_display()

    def get_sequencer(self,obj):
        return obj.get_sequencer_display()

# class UsedSequencingLibSerializer(serializers.ModelSerializer):
#     name = serializers.SerializerMethodField()
#     conc = serializers.SerializerMethodField()
#     vol_remain = serializers.SerializerMethodField()
#     frag_size = serializers.SerializerMethodField()
#     nm = serializers.SerializerMethodField()
#     nmol = serializers.SerializerMethodField()
#     target_vol = serializers.SerializerMethodField()
#
#     class Meta:
#         model = CL_SEQL_LINK
#         fields = ("id", "captured_lib", "name", "conc", "frag_size", "vol_remain", "nm", "nmol", "target_vol", "volume",)
#
#     def get_name(self, obj):
#         return obj.captured_lib.name
#
#     def get_conc(self, obj):
#         return obj.captured_lib.conc
#
#     def get_vol_remain(self, obj):
#         return obj.captured_lib.vol_remain
#
#     def get_frag_size(self, obj):
#         return obj.captured_lib.frag_size
#
#     def get_nm(self, obj):
#         return round(obj.captured_lib.nm,2)
#
#     def get_nmol(self,obj):
#         return obj.sequencing_lib.nmol
#
#     def get_target_vol(self,obj):
#         return obj.sequencing_lib.target_vol
