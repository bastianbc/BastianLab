# tests/unit/libprep/test_serializers.py
"""
Libprep Serializers Test Cases - No Database Required
"""
import pytest
from unittest.mock import Mock, MagicMock
from rest_framework import serializers
from tests.utils.base_test import BaseAPITestNoDatabase
from tests.fixtures.libprep_fixtures import LibprepTestData


class TestAreaLinksSerializer(BaseAPITestNoDatabase):
    """Test AreaLinksSerializer"""

    def test_serializer_initialization(self):
        """Test AreaLinksSerializer initializes correctly"""
        from libprep.serializers import AreaLinksSerializer

        serializer = AreaLinksSerializer()
        assert serializer is not None

    def test_serializer_inherits_from_model_serializer(self):
        """Test AreaLinksSerializer inherits from ModelSerializer"""
        from libprep.serializers import AreaLinksSerializer

        assert issubclass(AreaLinksSerializer, serializers.ModelSerializer)

    def test_serializer_meta_model(self):
        """Test serializer Meta.model is AREA_NA_LINK"""
        from libprep.serializers import AreaLinksSerializer
        from libprep.models import AREA_NA_LINK

        assert AreaLinksSerializer.Meta.model == AREA_NA_LINK

    def test_serializer_meta_fields(self):
        """Test serializer Meta.fields is __all__"""
        from libprep.serializers import AreaLinksSerializer

        assert AreaLinksSerializer.Meta.fields == '__all__'

    def test_serializer_has_area_field(self):
        """Test serializer has area SerializerMethodField"""
        from libprep.serializers import AreaLinksSerializer

        serializer = AreaLinksSerializer()
        assert 'area' in serializer.fields
        assert isinstance(serializer.fields['area'], serializers.SerializerMethodField)

    def test_get_area_with_area(self):
        """Test get_area returns tuple when area exists"""
        from libprep.serializers import AreaLinksSerializer

        # Mock area
        mock_area = Mock()
        mock_area.id = 1
        mock_area.name = 'BLK001_area1'

        # Mock link with area
        mock_link = Mock()
        mock_link.area = mock_area

        serializer = AreaLinksSerializer()
        result = serializer.get_area(mock_link)

        assert result == (1, 'BLK001_area1')

    def test_get_area_without_area(self):
        """Test get_area returns None when area is None"""
        from libprep.serializers import AreaLinksSerializer

        # Mock link without area
        mock_link = Mock()
        mock_link.area = None

        serializer = AreaLinksSerializer()
        result = serializer.get_area(mock_link)

        assert result is None


class TestNucacidsSerializer(BaseAPITestNoDatabase):
    """Test NucacidsSerializer"""

    def test_serializer_initialization(self):
        """Test NucacidsSerializer initializes correctly"""
        from libprep.serializers import NucacidsSerializer

        serializer = NucacidsSerializer()
        assert serializer is not None

    def test_serializer_inherits_from_model_serializer(self):
        """Test NucacidsSerializer inherits from ModelSerializer"""
        from libprep.serializers import NucacidsSerializer

        assert issubclass(NucacidsSerializer, serializers.ModelSerializer)

    def test_serializer_meta_model(self):
        """Test serializer Meta.model is NucAcids"""
        from libprep.serializers import NucacidsSerializer
        from libprep.models import NucAcids

        assert NucacidsSerializer.Meta.model == NucAcids

    def test_serializer_meta_fields(self):
        """Test serializer Meta.fields includes expected fields"""
        from libprep.serializers import NucacidsSerializer

        expected_fields = (
            "id", "name", "area_id", "area_na_links", "num_areas", "na_type",
            "na_type_label", "date", "method", "method_label", "conc",
            "vol_init", "vol_remain", "amount", "num_areas", "num_samplelibs", "DT_RowId",
        )
        assert NucacidsSerializer.Meta.fields == expected_fields

    def test_serializer_has_area_na_links_field(self):
        """Test serializer has area_na_links field"""
        from libprep.serializers import NucacidsSerializer

        serializer = NucacidsSerializer()
        assert 'area_na_links' in serializer.fields

    def test_serializer_has_dt_row_id_field(self):
        """Test serializer has DT_RowId SerializerMethodField"""
        from libprep.serializers import NucacidsSerializer

        serializer = NucacidsSerializer()
        assert 'DT_RowId' in serializer.fields
        assert isinstance(serializer.fields['DT_RowId'], serializers.SerializerMethodField)

    def test_serializer_has_area_id_field(self):
        """Test serializer has area_id SerializerMethodField"""
        from libprep.serializers import NucacidsSerializer

        serializer = NucacidsSerializer()
        assert 'area_id' in serializer.fields
        assert isinstance(serializer.fields['area_id'], serializers.SerializerMethodField)

    def test_serializer_has_num_areas_field(self):
        """Test serializer has num_areas IntegerField"""
        from libprep.serializers import NucacidsSerializer

        serializer = NucacidsSerializer()
        assert 'num_areas' in serializer.fields
        assert isinstance(serializer.fields['num_areas'], serializers.IntegerField)

    def test_serializer_has_method_label_field(self):
        """Test serializer has method_label SerializerMethodField"""
        from libprep.serializers import NucacidsSerializer

        serializer = NucacidsSerializer()
        assert 'method_label' in serializer.fields
        assert isinstance(serializer.fields['method_label'], serializers.SerializerMethodField)

    def test_serializer_has_na_type_label_field(self):
        """Test serializer has na_type_label SerializerMethodField"""
        from libprep.serializers import NucacidsSerializer

        serializer = NucacidsSerializer()
        assert 'na_type_label' in serializer.fields
        assert isinstance(serializer.fields['na_type_label'], serializers.SerializerMethodField)

    def test_serializer_has_vol_remain_field(self):
        """Test serializer has vol_remain SerializerMethodField"""
        from libprep.serializers import NucacidsSerializer

        serializer = NucacidsSerializer()
        assert 'vol_remain' in serializer.fields
        assert isinstance(serializer.fields['vol_remain'], serializers.SerializerMethodField)

    def test_serializer_has_amount_field(self):
        """Test serializer has amount SerializerMethodField"""
        from libprep.serializers import NucacidsSerializer

        serializer = NucacidsSerializer()
        assert 'amount' in serializer.fields
        assert isinstance(serializer.fields['amount'], serializers.SerializerMethodField)

    def test_serializer_has_num_samplelibs_field(self):
        """Test serializer has num_samplelibs IntegerField"""
        from libprep.serializers import NucacidsSerializer

        serializer = NucacidsSerializer()
        assert 'num_samplelibs' in serializer.fields
        assert isinstance(serializer.fields['num_samplelibs'], serializers.IntegerField)

    def test_get_dt_row_id_returns_object_id(self):
        """Test get_DT_RowId returns object id"""
        from libprep.serializers import NucacidsSerializer

        # Mock nucacid object
        mock_nucacid = Mock()
        mock_nucacid.id = 42

        serializer = NucacidsSerializer()
        result = serializer.get_DT_RowId(mock_nucacid)

        assert result == 42

    def test_get_method_label_with_method(self):
        """Test get_method_label returns method name when method exists"""
        from libprep.serializers import NucacidsSerializer

        # Mock method
        mock_method = Mock()
        mock_method.name = 'Extraction Method 1'

        # Mock nucacid with method
        mock_nucacid = Mock()
        mock_nucacid.method = mock_method

        serializer = NucacidsSerializer()
        result = serializer.get_method_label(mock_nucacid)

        assert result == 'Extraction Method 1'

    def test_get_method_label_without_method(self):
        """Test get_method_label returns None when method is None"""
        from libprep.serializers import NucacidsSerializer

        # Mock nucacid without method
        mock_nucacid = Mock()
        mock_nucacid.method = None

        serializer = NucacidsSerializer()
        result = serializer.get_method_label(mock_nucacid)

        assert result is None

    def test_get_na_type_label_returns_display(self):
        """Test get_na_type_label returns na_type display"""
        from libprep.serializers import NucacidsSerializer

        # Mock nucacid
        mock_nucacid = Mock()
        mock_nucacid.get_na_type_display.return_value = 'DNA'

        serializer = NucacidsSerializer()
        result = serializer.get_na_type_label(mock_nucacid)

        assert result == 'DNA'

    def test_get_area_id_returns_none(self):
        """Test get_area_id returns None"""
        from libprep.serializers import NucacidsSerializer

        mock_nucacid = Mock()

        serializer = NucacidsSerializer()
        result = serializer.get_area_id(mock_nucacid)

        assert result is None

    def test_get_vol_remain_returns_rounded_value(self):
        """Test get_vol_remain returns rounded value"""
        from libprep.serializers import NucacidsSerializer

        # Mock nucacid
        mock_nucacid = Mock()
        mock_nucacid.vol_remain = 45.678

        serializer = NucacidsSerializer()
        result = serializer.get_vol_remain(mock_nucacid)

        assert result == 45.68

    def test_get_amount_returns_rounded_value(self):
        """Test get_amount returns rounded amount"""
        from libprep.serializers import NucacidsSerializer

        # Mock nucacid
        mock_nucacid = Mock()
        mock_nucacid.amount = 127.8954

        serializer = NucacidsSerializer()
        result = serializer.get_amount(mock_nucacid)

        assert result == 127.90
