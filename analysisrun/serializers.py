from rest_framework import serializers
from .models import *
from urllib.parse import urlsplit


S3_BASE = "https://s3.us-west-2.amazonaws.com"

def _short_s3_or_local(url_or_path: str) -> str | None:
    if not url_or_path:
        return None

    if url_or_path.startswith("http"):
        parts = urlsplit(url_or_path)  # strips query/fragment for us
        host = parts.netloc
        path = parts.path.lstrip("/")

        # Path-style presign (what you have): s3.us-west-2.amazonaws.com/<bucket>/<key>
        if host == "s3.us-west-2.amazonaws.com":
            return f"{S3_BASE}/{path}"

        # Virtual-hosted-style: <bucket>.s3.us-west-2.amazonaws.com/<key>
        suffix = ".s3.us-west-2.amazonaws.com"
        if host.endswith(suffix):
            bucket = host[: -len(suffix)]
            key = parts.path.lstrip("/")
            return f"{S3_BASE}/{bucket}/{key}"

        # Non-S3 or something else → just drop the query
        return f"{parts.scheme}://{host}/{path}"

    # Local filesystem storage
    if url_or_path.startswith("/media/"):
        return url_or_path
    return "/" + url_or_path.lstrip("/")


class AnalysisRunSerializer(serializers.ModelSerializer):
    DT_RowId = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    sheet = serializers.SerializerMethodField()

    class Meta:
        model = AnalysisRun
        fields = ("id", "name", "pipeline", "genome", "date", "sheet", "status", "DT_RowId", )


    def get_sheet(self, obj):
        f = getattr(obj, "sheet", None)
        raw = ""
        # Prefer URL if available, fall back to "name" (key) or attr itself
        if hasattr(f, "url"):
            raw = f.url
        elif hasattr(f, "name"):
            raw = f.name
        else:
            raw = str(f or "")
        return _short_s3_or_local(raw)


    def get_DT_RowId(self, obj):
       return getattr(obj, 'id')

    def get_status(self, obj):
        return obj.get_status_display()
