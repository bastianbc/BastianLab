from rest_framework import serializers
from .models import *
from urllib.parse import urlsplit

class AnalysisRunSerializer(serializers.ModelSerializer):
    DT_RowId = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    sheet = serializers.SerializerMethodField()

    class Meta:
        model = AnalysisRun
        fields = ("id", "name", "pipeline", "genome", "date", "sheet", "status", "DT_RowId", )

    def get_sheet(self, obj):
        f = getattr(obj, "sheet", None)  # FileField
        if not f:
            return None
        # If it's an S3 URL, strip query and return just the path; else return relative name.
        val = str(getattr(f, "url", "") or getattr(f, "name", ""))
        parts = urlsplit(val)
        if parts.scheme in ("http", "https"):
            # return just the bucket key/path (leading slash for UI consistency)
            return "/" + parts.path.lstrip("/")
        # local storage: ensure it’s under MEDIA_URL for the UI
        return f"/{getattr(f, 'name', '').lstrip('/')}"

    def get_DT_RowId(self, obj):
       return getattr(obj, 'id')

    def get_status(self, obj):
        return obj.get_status_display()
