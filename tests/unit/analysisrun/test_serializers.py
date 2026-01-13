# tests/unit/analysisrun/test_serializers.py
"""
Analysisrun Serializers Test Cases - No Database Required
"""
import pytest
from unittest.mock import Mock, MagicMock
from rest_framework import serializers
from tests.utils.base_test import BaseAPITestNoDatabase
from tests.fixtures.analysisrun_fixtures import AnalysisrunTestData


class TestShortS3OrLocalHelper(BaseAPITestNoDatabase):
    """Test _short_s3_or_local helper function"""

    def test_helper_function_exists(self):
        """Test _short_s3_or_local function exists"""
        from analysisrun.serializers import _short_s3_or_local
        assert _short_s3_or_local is not None
        assert callable(_short_s3_or_local)

    def test_returns_none_for_empty_input(self):
        """Test returns None for empty input"""
        from analysisrun.serializers import _short_s3_or_local
        assert _short_s3_or_local(None) is None
        assert _short_s3_or_local("") is None

    def test_handles_path_style_s3_url(self):
        """Test handles path-style S3 URL"""
        from analysisrun.serializers import _short_s3_or_local

        url = "https://s3.us-west-2.amazonaws.com/bucket/key/file.csv"
        result = _short_s3_or_local(url)
        assert result.startswith("https://s3.us-west-2.amazonaws.com")

    def test_handles_local_media_path(self):
        """Test handles local /media/ path"""
        from analysisrun.serializers import _short_s3_or_local

        path = "/media/analysis/AR1.csv"
        result = _short_s3_or_local(path)
        assert result == "/media/analysis/AR1.csv"


class TestAnalysisRunSerializer(BaseAPITestNoDatabase):
    """Test AnalysisRunSerializer"""

    def test_serializer_initialization(self):
        """Test AnalysisRunSerializer initializes correctly"""
        from analysisrun.serializers import AnalysisRunSerializer

        serializer = AnalysisRunSerializer()
        assert serializer is not None

    def test_serializer_inherits_from_model_serializer(self):
        """Test AnalysisRunSerializer inherits from ModelSerializer"""
        from analysisrun.serializers import AnalysisRunSerializer

        assert issubclass(AnalysisRunSerializer, serializers.ModelSerializer)

    def test_serializer_meta_model(self):
        """Test serializer Meta.model is AnalysisRun"""
        from analysisrun.serializers import AnalysisRunSerializer
        from analysisrun.models import AnalysisRun

        assert AnalysisRunSerializer.Meta.model == AnalysisRun

    def test_serializer_meta_fields(self):
        """Test serializer Meta.fields contains expected fields"""
        from analysisrun.serializers import AnalysisRunSerializer

        expected_fields = ("id", "name", "pipeline", "genome", "date", "sheet", "status", "DT_RowId")
        assert AnalysisRunSerializer.Meta.fields == expected_fields

    def test_serializer_has_dt_row_id_field(self):
        """Test serializer has DT_RowId SerializerMethodField"""
        from analysisrun.serializers import AnalysisRunSerializer

        serializer = AnalysisRunSerializer()
        assert 'DT_RowId' in serializer.fields
        assert isinstance(serializer.fields['DT_RowId'], serializers.SerializerMethodField)

    def test_serializer_has_status_field(self):
        """Test serializer has status SerializerMethodField"""
        from analysisrun.serializers import AnalysisRunSerializer

        serializer = AnalysisRunSerializer()
        assert 'status' in serializer.fields
        assert isinstance(serializer.fields['status'], serializers.SerializerMethodField)

    def test_serializer_has_sheet_field(self):
        """Test serializer has sheet SerializerMethodField"""
        from analysisrun.serializers import AnalysisRunSerializer

        serializer = AnalysisRunSerializer()
        assert 'sheet' in serializer.fields
        assert isinstance(serializer.fields['sheet'], serializers.SerializerMethodField)

    def test_get_dt_row_id_returns_object_id(self):
        """Test get_DT_RowId returns object id"""
        from analysisrun.serializers import AnalysisRunSerializer

        mock_analysisrun = Mock()
        mock_analysisrun.id = 42

        serializer = AnalysisRunSerializer()
        result = serializer.get_DT_RowId(mock_analysisrun)

        assert result == 42

    def test_get_status_returns_display_value(self):
        """Test get_status returns display value"""
        from analysisrun.serializers import AnalysisRunSerializer

        mock_analysisrun = Mock()
        mock_analysisrun.get_status_display.return_value = 'Pending'

        serializer = AnalysisRunSerializer()
        result = serializer.get_status(mock_analysisrun)

        assert result == 'Pending'

    def test_get_sheet_with_url_attribute(self):
        """Test get_sheet returns URL when available"""
        from analysisrun.serializers import AnalysisRunSerializer

        mock_file = Mock()
        mock_file.url = "/media/analysis/AR1.csv"

        mock_analysisrun = Mock()
        mock_analysisrun.sheet = mock_file

        serializer = AnalysisRunSerializer()
        result = serializer.get_sheet(mock_analysisrun)

        assert result is not None

    def test_get_sheet_with_name_attribute(self):
        """Test get_sheet returns name when URL not available"""
        from analysisrun.serializers import AnalysisRunSerializer

        mock_file = Mock(spec=['name'])
        mock_file.name = "AR1.csv"
        del mock_file.url

        mock_analysisrun = Mock()
        mock_analysisrun.sheet = mock_file

        serializer = AnalysisRunSerializer()
        result = serializer.get_sheet(mock_analysisrun)

        assert result is not None

    def test_get_sheet_with_none_value(self):
        """Test get_sheet handles None value"""
        from analysisrun.serializers import AnalysisRunSerializer

        mock_analysisrun = Mock()
        mock_analysisrun.sheet = None

        serializer = AnalysisRunSerializer()
        result = serializer.get_sheet(mock_analysisrun)

        assert result is None
