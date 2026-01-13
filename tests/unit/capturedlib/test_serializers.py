# tests/unit/capturedlib/test_serializers.py
"""
Capturedlib Serializers Test Cases - No Database Required
"""
import pytest
from unittest.mock import Mock, MagicMock
from rest_framework import serializers
from tests.utils.base_test import BaseAPITestNoDatabase
from tests.fixtures.capturedlib_fixtures import CapturedlibTestData


class TestCapturedLibSerializer(BaseAPITestNoDatabase):
    """Test CapturedLibSerializer"""

    def test_serializer_initialization(self):
        """Test CapturedLibSerializer initializes correctly"""
        from capturedlib.serializers import CapturedLibSerializer

        serializer = CapturedLibSerializer()
        assert serializer is not None

    def test_serializer_inherits_from_model_serializer(self):
        """Test CapturedLibSerializer inherits from ModelSerializer"""
        from capturedlib.serializers import CapturedLibSerializer

        assert issubclass(CapturedLibSerializer, serializers.ModelSerializer)

    def test_serializer_meta_model(self):
        """Test serializer Meta.model is CapturedLib"""
        from capturedlib.serializers import CapturedLibSerializer
        from capturedlib.models import CapturedLib

        assert CapturedLibSerializer.Meta.model == CapturedLib

    def test_serializer_has_dt_row_id_field(self):
        """Test serializer has DT_RowId SerializerMethodField"""
        from capturedlib.serializers import CapturedLibSerializer

        serializer = CapturedLibSerializer()
        assert 'DT_RowId' in serializer.fields
        assert isinstance(serializer.fields['DT_RowId'], serializers.SerializerMethodField)

    def test_serializer_has_bait_label_field(self):
        """Test serializer has bait_label SerializerMethodField"""
        from capturedlib.serializers import CapturedLibSerializer

        serializer = CapturedLibSerializer()
        assert 'bait_label' in serializer.fields
        assert isinstance(serializer.fields['bait_label'], serializers.SerializerMethodField)

    def test_serializer_has_buffer_label_field(self):
        """Test serializer has buffer_label SerializerMethodField"""
        from capturedlib.serializers import CapturedLibSerializer

        serializer = CapturedLibSerializer()
        assert 'buffer_label' in serializer.fields
        assert isinstance(serializer.fields['buffer_label'], serializers.SerializerMethodField)

    def test_serializer_has_num_samplelibs_field(self):
        """Test serializer has num_samplelibs IntegerField"""
        from capturedlib.serializers import CapturedLibSerializer

        serializer = CapturedLibSerializer()
        assert 'num_samplelibs' in serializer.fields
        assert isinstance(serializer.fields['num_samplelibs'], serializers.IntegerField)

    def test_serializer_has_num_sequencinglibs_field(self):
        """Test serializer has num_sequencinglibs IntegerField"""
        from capturedlib.serializers import CapturedLibSerializer

        serializer = CapturedLibSerializer()
        assert 'num_sequencinglibs' in serializer.fields
        assert isinstance(serializer.fields['num_sequencinglibs'], serializers.IntegerField)

    def test_get_dt_row_id_returns_object_id(self):
        """Test get_DT_RowId returns object id"""
        from capturedlib.serializers import CapturedLibSerializer

        mock_capturedlib = Mock()
        mock_capturedlib.id = 42

        serializer = CapturedLibSerializer()
        result = serializer.get_DT_RowId(mock_capturedlib)

        assert result == 42

    def test_get_bait_label_with_bait(self):
        """Test get_bait_label returns bait name when bait exists"""
        from capturedlib.serializers import CapturedLibSerializer

        mock_bait = Mock()
        mock_bait.name = 'Bait 1'

        mock_capturedlib = Mock()
        mock_capturedlib.bait = mock_bait

        serializer = CapturedLibSerializer()
        result = serializer.get_bait_label(mock_capturedlib)

        assert result == 'Bait 1'

    def test_get_bait_label_without_bait(self):
        """Test get_bait_label returns None when bait is None"""
        from capturedlib.serializers import CapturedLibSerializer

        mock_capturedlib = Mock()
        mock_capturedlib.bait = None

        serializer = CapturedLibSerializer()
        result = serializer.get_bait_label(mock_capturedlib)

        assert result is None

    def test_get_buffer_label_with_buffer(self):
        """Test get_buffer_label returns buffer name when buffer exists"""
        from capturedlib.serializers import CapturedLibSerializer

        mock_buffer = Mock()
        mock_buffer.name = 'Buffer 1'

        mock_capturedlib = Mock()
        mock_capturedlib.buffer = mock_buffer

        serializer = CapturedLibSerializer()
        result = serializer.get_buffer_label(mock_capturedlib)

        assert result == 'Buffer 1'

    def test_get_buffer_label_without_buffer(self):
        """Test get_buffer_label returns None when buffer is None"""
        from capturedlib.serializers import CapturedLibSerializer

        mock_capturedlib = Mock()
        mock_capturedlib.buffer = None

        serializer = CapturedLibSerializer()
        result = serializer.get_buffer_label(mock_capturedlib)

        assert result is None


class TestUsedSampleLibSerializer(BaseAPITestNoDatabase):
    """Test UsedSampleLibSerializer"""

    def test_serializer_initialization(self):
        """Test UsedSampleLibSerializer initializes correctly"""
        from capturedlib.serializers import UsedSampleLibSerializer

        serializer = UsedSampleLibSerializer()
        assert serializer is not None

    def test_serializer_inherits_from_model_serializer(self):
        """Test UsedSampleLibSerializer inherits from ModelSerializer"""
        from capturedlib.serializers import UsedSampleLibSerializer

        assert issubclass(UsedSampleLibSerializer, serializers.ModelSerializer)

    def test_serializer_meta_model(self):
        """Test serializer Meta.model is SL_CL_LINK"""
        from capturedlib.serializers import UsedSampleLibSerializer
        from capturedlib.models import SL_CL_LINK

        assert UsedSampleLibSerializer.Meta.model == SL_CL_LINK

    def test_serializer_has_id_field(self):
        """Test serializer has id SerializerMethodField"""
        from capturedlib.serializers import UsedSampleLibSerializer

        serializer = UsedSampleLibSerializer()
        assert 'id' in serializer.fields
        assert isinstance(serializer.fields['id'], serializers.SerializerMethodField)

    def test_serializer_has_name_field(self):
        """Test serializer has name SerializerMethodField"""
        from capturedlib.serializers import UsedSampleLibSerializer

        serializer = UsedSampleLibSerializer()
        assert 'name' in serializer.fields
        assert isinstance(serializer.fields['name'], serializers.SerializerMethodField)

    def test_serializer_has_conc_field(self):
        """Test serializer has conc SerializerMethodField"""
        from capturedlib.serializers import UsedSampleLibSerializer

        serializer = UsedSampleLibSerializer()
        assert 'conc' in serializer.fields
        assert isinstance(serializer.fields['conc'], serializers.SerializerMethodField)

    def test_serializer_has_vol_remain_field(self):
        """Test serializer has vol_remain SerializerMethodField"""
        from capturedlib.serializers import UsedSampleLibSerializer

        serializer = UsedSampleLibSerializer()
        assert 'vol_remain' in serializer.fields
        assert isinstance(serializer.fields['vol_remain'], serializers.SerializerMethodField)

    def test_serializer_has_barcode_field(self):
        """Test serializer has barcode SerializerMethodField"""
        from capturedlib.serializers import UsedSampleLibSerializer

        serializer = UsedSampleLibSerializer()
        assert 'barcode' in serializer.fields
        assert isinstance(serializer.fields['barcode'], serializers.SerializerMethodField)

    def test_serializer_has_volume_field(self):
        """Test serializer has volume FloatField"""
        from capturedlib.serializers import UsedSampleLibSerializer

        serializer = UsedSampleLibSerializer()
        assert 'volume' in serializer.fields
        assert isinstance(serializer.fields['volume'], serializers.FloatField)

    def test_get_id_returns_sample_lib_id(self):
        """Test get_id returns sample_lib id"""
        from capturedlib.serializers import UsedSampleLibSerializer

        mock_sl = Mock()
        mock_sl.id = 42

        mock_link = Mock()
        mock_link.sample_lib = mock_sl

        serializer = UsedSampleLibSerializer()
        result = serializer.get_id(mock_link)

        assert result == 42

    def test_get_name_returns_sample_lib_name(self):
        """Test get_name returns sample_lib name"""
        from capturedlib.serializers import UsedSampleLibSerializer

        mock_sl = Mock()
        mock_sl.name = 'SL-001'

        mock_link = Mock()
        mock_link.sample_lib = mock_sl

        serializer = UsedSampleLibSerializer()
        result = serializer.get_name(mock_link)

        assert result == 'SL-001'

    def test_get_conc_returns_sample_lib_qpcr_conc(self):
        """Test get_conc returns sample_lib qpcr_conc"""
        from capturedlib.serializers import UsedSampleLibSerializer

        mock_sl = Mock()
        mock_sl.qpcr_conc = 25.5

        mock_link = Mock()
        mock_link.sample_lib = mock_sl

        serializer = UsedSampleLibSerializer()
        result = serializer.get_conc(mock_link)

        assert result == 25.5

    def test_get_vol_remain_returns_sample_lib_vol_remain(self):
        """Test get_vol_remain returns sample_lib vol_remain"""
        from capturedlib.serializers import UsedSampleLibSerializer

        mock_sl = Mock()
        mock_sl.vol_remain = 45.0

        mock_link = Mock()
        mock_link.sample_lib = mock_sl

        serializer = UsedSampleLibSerializer()
        result = serializer.get_vol_remain(mock_link)

        assert result == 45.0

    def test_get_barcode_with_barcode(self):
        """Test get_barcode returns barcode name when barcode exists"""
        from capturedlib.serializers import UsedSampleLibSerializer

        mock_barcode = Mock()
        mock_barcode.name = 'BC-001'

        mock_sl = Mock()
        mock_sl.barcode = mock_barcode

        mock_link = Mock()
        mock_link.sample_lib = mock_sl

        serializer = UsedSampleLibSerializer()
        result = serializer.get_barcode(mock_link)

        assert result == 'BC-001'

    def test_get_barcode_without_barcode(self):
        """Test get_barcode returns None when barcode is None"""
        from capturedlib.serializers import UsedSampleLibSerializer

        mock_sl = Mock()
        mock_sl.barcode = None

        mock_link = Mock()
        mock_link.sample_lib = mock_sl

        serializer = UsedSampleLibSerializer()
        result = serializer.get_barcode(mock_link)

        assert result is None
