from rest_framework import serializers
from .models import *

class CnsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cns
        fields = ("id","sample_lib","sequencing_run","variant_file","analysis_run","chromosome","start","end","gene","depth","ci-hi","ci_lo","cn","log2","p_bintest","p_ttest","probes","weight","DT_RowId",)
