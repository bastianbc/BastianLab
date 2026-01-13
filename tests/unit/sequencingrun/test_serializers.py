# tests/unit/sequencingrun/test_serializers.py
"""
Sequencingrun Serializers Test Cases - No Database Required
"""
import pytest
from unittest.mock import Mock, MagicMock
from rest_framework import serializers
from tests.utils.base_test import BaseAPITestNoDatabase
from tests.fixtures.sequencingrun_fixtures import SequencingrunTestData


class TestSequencingRunSerializer(BaseAPITestNoDatabase):
    """Test SequencingRunSerializer"""

    def test_serializer_initialization(self):
        """Test SequencingRunSerializer initializes correctly"""
        from sequencingrun.serializers import SequencingRunSerializer

        serializer = SequencingRunSerializer()
        assert serializer is not None

    def test_serializer_inherits_from_model_serializer(self):
        """Test SequencingRunSerializer inherits from ModelSerializer"""
        from sequencingrun.serializers import SequencingRunSerializer

        assert issubclass(SequencingRunSerializer, serializers.ModelSerializer)

    def test_serializer_meta_model(self):
        """Test serializer Meta.model is SequencingRun"""
        from sequencingrun.serializers import SequencingRunSerializer
        from sequencingrun.models import SequencingRun

        assert SequencingRunSerializer.Meta.model == SequencingRun

    def test_serializer_has_dt_row_id_field(self):
        """Test serializer has DT_RowId SerializerMethodField"""
        from sequencingrun.serializers import SequencingRunSerializer

        serializer = SequencingRunSerializer()
        assert 'DT_RowId' in serializer.fields
        assert isinstance(serializer.fields['DT_RowId'], serializers.SerializerMethodField)

    def test_serializer_has_facility_label_field(self):
        """Test serializer has facility_label SerializerMethodField"""
        from sequencingrun.serializers import SequencingRunSerializer

        serializer = SequencingRunSerializer()
        assert 'facility_label' in serializer.fields
        assert isinstance(serializer.fields['facility_label'], serializers.SerializerMethodField)

    def test_serializer_has_sequencer_label_field(self):
        """Test serializer has sequencer_label SerializerMethodField"""
        from sequencingrun.serializers import SequencingRunSerializer

        serializer = SequencingRunSerializer()
        assert 'sequencer_label' in serializer.fields
        assert isinstance(serializer.fields['sequencer_label'], serializers.SerializerMethodField)

    def test_serializer_has_pe_label_field(self):
        """Test serializer has pe_label SerializerMethodField"""
        from sequencingrun.serializers import SequencingRunSerializer

        serializer = SequencingRunSerializer()
        assert 'pe_label' in serializer.fields
        assert isinstance(serializer.fields['pe_label'], serializers.SerializerMethodField)

    def test_serializer_has_num_sequencinglibs_field(self):
        """Test serializer has num_sequencinglibs IntegerField"""
        from sequencingrun.serializers import SequencingRunSerializer

        serializer = SequencingRunSerializer()
        assert 'num_sequencinglibs' in serializer.fields
        assert isinstance(serializer.fields['num_sequencinglibs'], serializers.IntegerField)

    def test_serializer_has_num_file_sets_field(self):
        """Test serializer has num_file_sets IntegerField"""
        from sequencingrun.serializers import SequencingRunSerializer

        serializer = SequencingRunSerializer()
        assert 'num_file_sets' in serializer.fields
        assert isinstance(serializer.fields['num_file_sets'], serializers.IntegerField)

    def test_get_dt_row_id_returns_object_id(self):
        """Test get_DT_RowId returns object id"""
        from sequencingrun.serializers import SequencingRunSerializer

        mock_sequencingrun = Mock()
        mock_sequencingrun.id = 42

        serializer = SequencingRunSerializer()
        result = serializer.get_DT_RowId(mock_sequencingrun)

        assert result == 42

    def test_get_facility_label_returns_display_value(self):
        """Test get_facility_label returns display value"""
        from sequencingrun.serializers import SequencingRunSerializer

        mock_sequencingrun = Mock()
        mock_sequencingrun.get_facility_display.return_value = 'CAT'

        serializer = SequencingRunSerializer()
        result = serializer.get_facility_label(mock_sequencingrun)

        assert result == 'CAT'

    def test_get_sequencer_label_returns_display_value(self):
        """Test get_sequencer_label returns display value"""
        from sequencingrun.serializers import SequencingRunSerializer

        mock_sequencingrun = Mock()
        mock_sequencingrun.get_sequencer_display.return_value = 'NovaSeq 6000 S4'

        serializer = SequencingRunSerializer()
        result = serializer.get_sequencer_label(mock_sequencingrun)

        assert result == 'NovaSeq 6000 S4'

    def test_get_pe_label_returns_display_value(self):
        """Test get_pe_label returns display value"""
        from sequencingrun.serializers import SequencingRunSerializer

        mock_sequencingrun = Mock()
        mock_sequencingrun.get_pe_display.return_value = 'PE 150'

        serializer = SequencingRunSerializer()
        result = serializer.get_pe_label(mock_sequencingrun)

        assert result == 'PE 150'


class TestUsedSequencingLibSerializer(BaseAPITestNoDatabase):
    """Test UsedSequencingLibSerializer"""

    def test_serializer_initialization(self):
        """Test UsedSequencingLibSerializer initializes correctly"""
        from sequencingrun.serializers import UsedSequencingLibSerializer

        serializer = UsedSequencingLibSerializer()
        assert serializer is not None

    def test_serializer_inherits_from_model_serializer(self):
        """Test UsedSequencingLibSerializer inherits from ModelSerializer"""
        from sequencingrun.serializers import UsedSequencingLibSerializer

        assert issubclass(UsedSequencingLibSerializer, serializers.ModelSerializer)

    def test_serializer_has_buffer_field(self):
        """Test serializer has buffer SerializerMethodField"""
        from sequencingrun.serializers import UsedSequencingLibSerializer

        serializer = UsedSequencingLibSerializer()
        assert 'buffer' in serializer.fields
        assert isinstance(serializer.fields['buffer'], serializers.SerializerMethodField)

    def test_get_buffer_returns_display_value(self):
        """Test get_buffer returns display value"""
        from sequencingrun.serializers import UsedSequencingLibSerializer

        mock_seqlib = Mock()
        mock_seqlib.get_buffer_display.return_value = 'TE'

        serializer = UsedSequencingLibSerializer()
        result = serializer.get_buffer(mock_seqlib)

        assert result == 'TE'


class TestSingleSequencingRunSerializer(BaseAPITestNoDatabase):
    """Test SingleSequencingRunSerializer"""

    def test_serializer_initialization(self):
        """Test SingleSequencingRunSerializer initializes correctly"""
        from sequencingrun.serializers import SingleSequencingRunSerializer

        serializer = SingleSequencingRunSerializer()
        assert serializer is not None

    def test_serializer_inherits_from_model_serializer(self):
        """Test SingleSequencingRunSerializer inherits from ModelSerializer"""
        from sequencingrun.serializers import SingleSequencingRunSerializer

        assert issubclass(SingleSequencingRunSerializer, serializers.ModelSerializer)

    def test_serializer_meta_model(self):
        """Test serializer Meta.model is SequencingRun"""
        from sequencingrun.serializers import SingleSequencingRunSerializer
        from sequencingrun.models import SequencingRun

        assert SingleSequencingRunSerializer.Meta.model == SequencingRun

    def test_serializer_meta_fields(self):
        """Test serializer Meta.fields is __all__"""
        from sequencingrun.serializers import SingleSequencingRunSerializer

        assert SingleSequencingRunSerializer.Meta.fields == "__all__"
