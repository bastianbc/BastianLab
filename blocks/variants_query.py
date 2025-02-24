from django.db.models import F, Value, When, Case, ExpressionWrapper, FloatField
from variant.models import VariantCall, PVariant
from rest_framework import serializers


class VariantCustomSerializer(serializers.ModelSerializer):
    DT_RowId = serializers.SerializerMethodField()
    blocks = serializers.CharField(read_only=True)
    areas = serializers.CharField(read_only=True)
    genes = serializers.CharField(read_only=True)
    sample_lib = serializers.SerializerMethodField()
    vaf = serializers.FloatField()
    p_variant = serializers.CharField(read_only=True)

    class Meta:
        model = VariantCall
        fields = ("id", "areas", "sample_lib", "genes", "DT_RowId", "coverage", "vaf", "analysis_run", "blocks",  "p_variant")

    def get_DT_RowId(self, obj):
       return getattr(obj, 'id')

    def get_sample_lib(self,obj):
        return obj.sample_lib.name



def variant_queryset(block):
    return VariantCall.objects.filter(sample_lib__na_sl_links__nucacid__area_na_links__area__block=block).annotate(
                areas=F('sample_lib__na_sl_links__nucacid__area_na_links__area__name'),
                genes=F('g_variants__c_variants__gene__name'),
                p_variant=F('g_variants__c_variants__p_variants__name_meta'),
                vaf=ExpressionWrapper(
                    Case(
                        When(ref_read__gt=0, then=(F('alt_read') * 100.0) / (F('ref_read') + F('alt_read'))),
                        default=Value(0.0),
                        output_field=FloatField(),
                    ),
                    output_field=FloatField()
                )
    )