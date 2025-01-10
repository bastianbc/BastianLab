from rest_framework import serializers
from .models import *
from samplelib.models import SampleLib
from sequencingrun.models import SequencingRun
from analysisrun.models import AnalysisRun

class SequencingRunSerializerManual(serializers.ModelSerializer):
    class Meta:
        model = SequencingRun
        fields = ("name",)

class SampleLibSerializerManual(serializers.ModelSerializer):
    class Meta:
        model = SampleLib
        fields = ("name",)


class AnalysisRunSerializerManual(serializers.ModelSerializer):
    class Meta:
        model = AnalysisRun
        fields = ("name",)


class CnsSerializer(serializers.ModelSerializer):
    sequencing_run = SequencingRunSerializerManual(read_only=True)
    sample_lib = SampleLibSerializerManual(read_only=True)
    analysis_run = AnalysisRunSerializerManual(read_only=True)

    class Meta:
        model = Cns
        fields = ("id","sample_lib","sequencing_run","analysis_run","chromosome","start","end","gene","log2")

