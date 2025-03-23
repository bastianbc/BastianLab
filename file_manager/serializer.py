from rest_framework import serializers



class FileDirectorySerializer(serializers.Serializer):
    """Serializer for files and directories"""
    id = serializers.IntegerField()
    name = serializers.CharField()
    status = serializers.CharField()
    variant_file = serializers.CharField()
    type = serializers.ChoiceField(choices=['file', 'directory'])
    size = serializers.IntegerField(required=False, allow_null=True)
    dir = serializers.CharField()

