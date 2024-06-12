from rest_framework import serializers
from .models import *

class BarcodesetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Barcodeset
        fields = "__all__"

class BarcodeSerializer(serializers.ModelSerializer):
    DT_RowId = serializers.SerializerMethodField()
    class Meta:
        model = Barcode
        fields = ("id", "name", "i5", "i7", "DT_RowId",)

    def get_DT_RowId(self, obj):
       return getattr(obj, 'id')
