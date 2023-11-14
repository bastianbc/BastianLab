from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class ProjectsSerializer(serializers.ModelSerializer):
    DT_RowId = serializers.SerializerMethodField()
    num_blocks = serializers.IntegerField()
    pi_label = serializers.SerializerMethodField()
    technician = UserSerializer(many=True)
    researcher = UserSerializer(many=True)

    class Meta:
        model = Projects
        fields = ("abbreviation","name","technician","researcher","pi","pi_label","date_start","speedtype","pr_id","num_blocks","DT_RowId",)

    def get_DT_RowId(self, obj):
        return getattr(obj, 'pr_id')

    def get_pi_label(self,obj):
        return obj.get_pi_display()


