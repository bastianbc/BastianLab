# tests/unit/samplelib/test_serializers.py
"""
Samplelib Serializers Test Cases - No Database Required
"""
import pytest
from unittest.mock import Mock, MagicMock
from rest_framework import serializers
from tests.utils.base_test import BaseAPITestNoDatabase
from tests.fixtures.samplelib_fixtures import SamplelibTestData


class TestSampleLibSerializer(BaseAPITestNoDatabase):
    """Test SampleLibSerializer"""

    def test_serializer_initialization(self):
        """Test SampleLibSerializer initializes correctly"""
        from samplelib.serializers import SampleLibSerializer

        serializer = SampleLibSerializer()
        assert serializer is not None

    def test_serializer_inherits_from_model_serializer(self):
        """Test SampleLibSerializer inherits from ModelSerializer"""
        from samplelib.serializers import SampleLibSerializer

        assert issubclass(SampleLibSerializer, serializers.ModelSerializer)

    def test_serializer_meta_model(self):
        """Test serializer Meta.model is SampleLib"""
        from samplelib.serializers import SampleLibSerializer
        from samplelib.models import SampleLib

        assert SampleLibSerializer.Meta.model == SampleLib

    def test_serializer_has_dt_row_id_field(self):
        """Test serializer has DT_RowId SerializerMethodField"""
        from samplelib.serializers import SampleLibSerializer

        serializer = SampleLibSerializer()
        assert 'DT_RowId' in serializer.fields
        assert isinstance(serializer.fields['DT_RowId'], serializers.SerializerMethodField)

    def test_serializer_has_method_label_field(self):
        """Test serializer has method_label SerializerMethodField"""
        from samplelib.serializers import SampleLibSerializer

        serializer = SampleLibSerializer()
        assert 'method_label' in serializer.fields

    def test_serializer_has_amount_in_field(self):
        """Test serializer has amount_in SerializerMethodField"""
        from samplelib.serializers import SampleLibSerializer

        serializer = SampleLibSerializer()
        assert 'amount_in' in serializer.fields

    def test_serializer_has_amount_final_field(self):
        """Test serializer has amount_final SerializerMethodField"""
        from samplelib.serializers import SampleLibSerializer

        serializer = SampleLibSerializer()
        assert 'amount_final' in serializer.fields

    def test_get_dt_row_id_returns_object_id(self):
        """Test get_DT_RowId returns object id"""
        from samplelib.serializers import SampleLibSerializer

        mock_samplelib = Mock()
        mock_samplelib.id = 42

        serializer = SampleLibSerializer()
        result = serializer.get_DT_RowId(mock_samplelib)

        assert result == 42

    def test_get_method_label_with_method(self):
        """Test get_method_label returns method name when method exists"""
        from samplelib.serializers import SampleLibSerializer

        mock_method = Mock()
        mock_method.name = 'Method 1'

        mock_samplelib = Mock()
        mock_samplelib.method = mock_method

        serializer = SampleLibSerializer()
        result = serializer.get_method_label(mock_samplelib)

        assert result == 'Method 1'

    def test_get_method_label_without_method(self):
        """Test get_method_label returns None when method is None"""
        from samplelib.serializers import SampleLibSerializer

        mock_samplelib = Mock()
        mock_samplelib.method = None

        serializer = SampleLibSerializer()
        result = serializer.get_method_label(mock_samplelib)

        assert result is None

    def test_get_amount_in_returns_rounded_value(self):
        """Test get_amount_in returns rounded value"""
        from samplelib.serializers import SampleLibSerializer

        mock_samplelib = Mock()
        mock_samplelib.amount_in = 127.8954

        serializer = SampleLibSerializer()
        result = serializer.get_amount_in(mock_samplelib)

        assert result == 127.90

    def test_get_amount_final_returns_rounded_value(self):
        """Test get_amount_final returns rounded amount"""
        from samplelib.serializers import SampleLibSerializer

        mock_samplelib = Mock()
        mock_samplelib.amount_final = 95.456

        serializer = SampleLibSerializer()
        result = serializer.get_amount_final(mock_samplelib)

        assert result == 95.46


class TestUsedNuacidsSerializer(BaseAPITestNoDatabase):
    """Test UsedNuacidsSerializer"""

    def test_serializer_initialization(self):
        """Test UsedNuacidsSerializer initializes correctly"""
        from samplelib.serializers import UsedNuacidsSerializer

        serializer = UsedNuacidsSerializer()
        assert serializer is not None

    def test_serializer_inherits_from_model_serializer(self):
        """Test UsedNuacidsSerializer inherits from ModelSerializer"""
        from samplelib.serializers import UsedNuacidsSerializer

        assert issubclass(UsedNuacidsSerializer, serializers.ModelSerializer)

    def test_serializer_meta_model(self):
        """Test serializer Meta.model is NA_SL_LINK"""
        from samplelib.serializers import UsedNuacidsSerializer
        from samplelib.models import NA_SL_LINK

        assert UsedNuacidsSerializer.Meta.model == NA_SL_LINK

    def test_get_sample_lib_id_returns_id(self):
        """Test get_sample_lib_id returns sample_lib id"""
        from samplelib.serializers import UsedNuacidsSerializer

        mock_sl = Mock()
        mock_sl.id = 42

        mock_link = Mock()
        mock_link.sample_lib = mock_sl

        serializer = UsedNuacidsSerializer()
        result = serializer.get_sample_lib_id(mock_link)

        assert result == 42

    def test_get_sample_lib_name_returns_name(self):
        """Test get_sample_lib_name returns sample_lib name"""
        from samplelib.serializers import UsedNuacidsSerializer

        mock_sl = Mock()
        mock_sl.name = 'SL-001'

        mock_link = Mock()
        mock_link.sample_lib = mock_sl

        serializer = UsedNuacidsSerializer()
        result = serializer.get_sample_lib_name(mock_link)

        assert result == 'SL-001'


class TestSavedNuacidsSerializer(BaseAPITestNoDatabase):
    """Test SavedNuacidsSerializer"""

    def test_serializer_initialization(self):
        """Test SavedNuacidsSerializer initializes correctly"""
        from samplelib.serializers import SavedNuacidsSerializer

        serializer = SavedNuacidsSerializer()
        assert serializer is not None

    def test_serializer_inherits_from_model_serializer(self):
        """Test SavedNuacidsSerializer inherits from ModelSerializer"""
        from samplelib.serializers import SavedNuacidsSerializer

        assert issubclass(SavedNuacidsSerializer, serializers.ModelSerializer)

    def test_serializer_meta_model(self):
        """Test serializer Meta.model is NA_SL_LINK"""
        from samplelib.serializers import SavedNuacidsSerializer
        from samplelib.models import NA_SL_LINK

        assert SavedNuacidsSerializer.Meta.model == NA_SL_LINK
