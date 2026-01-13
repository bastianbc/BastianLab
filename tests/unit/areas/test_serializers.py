# tests/unit/areas/test_serializers.py
"""
Areas Serializers Test Cases - No Database Required
"""
import pytest
from unittest.mock import Mock, MagicMock
from rest_framework import serializers
from tests.utils.base_test import BaseAPITestNoDatabase
from tests.fixtures.areas_fixtures import AreasTestData


class TestAreasSerializer(BaseAPITestNoDatabase):
    """Test AreasSerializer"""

    def test_serializer_initialization(self):
        """Test AreasSerializer initializes correctly"""
        from areas.serializers import AreasSerializer

        serializer = AreasSerializer()
        assert serializer is not None

    def test_serializer_inherits_from_model_serializer(self):
        """Test AreasSerializer inherits from ModelSerializer"""
        from areas.serializers import AreasSerializer

        assert issubclass(AreasSerializer, serializers.ModelSerializer)

    def test_serializer_meta_model(self):
        """Test serializer Meta.model is Area"""
        from areas.serializers import AreasSerializer
        from areas.models import Area

        assert AreasSerializer.Meta.model == Area

    def test_serializer_meta_fields(self):
        """Test serializer Meta.fields includes expected fields"""
        from areas.serializers import AreasSerializer

        expected_fields = (
            "id", "name", "num_blocks", "num_projects", "area_type", "area_type_label",
            "completion_date", "investigator", "num_nucacids", "num_samplelibs",
            "DT_RowId", "num_variants",
        )
        assert AreasSerializer.Meta.fields == expected_fields

    def test_serializer_has_num_nucacids_field(self):
        """Test serializer has num_nucacids IntegerField"""
        from areas.serializers import AreasSerializer

        serializer = AreasSerializer()
        assert 'num_nucacids' in serializer.fields
        assert isinstance(serializer.fields['num_nucacids'], serializers.IntegerField)

    def test_serializer_has_num_variants_field(self):
        """Test serializer has num_variants IntegerField"""
        from areas.serializers import AreasSerializer

        serializer = AreasSerializer()
        assert 'num_variants' in serializer.fields
        assert isinstance(serializer.fields['num_variants'], serializers.IntegerField)

    def test_serializer_has_dt_row_id_method_field(self):
        """Test serializer has DT_RowId SerializerMethodField"""
        from areas.serializers import AreasSerializer

        serializer = AreasSerializer()
        assert 'DT_RowId' in serializer.fields
        assert isinstance(serializer.fields['DT_RowId'], serializers.SerializerMethodField)

    def test_serializer_has_num_blocks_field(self):
        """Test serializer has num_blocks IntegerField"""
        from areas.serializers import AreasSerializer

        serializer = AreasSerializer()
        assert 'num_blocks' in serializer.fields
        assert isinstance(serializer.fields['num_blocks'], serializers.IntegerField)

    def test_serializer_has_num_projects_field(self):
        """Test serializer has num_projects IntegerField"""
        from areas.serializers import AreasSerializer

        serializer = AreasSerializer()
        assert 'num_projects' in serializer.fields
        assert isinstance(serializer.fields['num_projects'], serializers.IntegerField)

    def test_serializer_has_investigator_method_field(self):
        """Test serializer has investigator SerializerMethodField"""
        from areas.serializers import AreasSerializer

        serializer = AreasSerializer()
        assert 'investigator' in serializer.fields
        assert isinstance(serializer.fields['investigator'], serializers.SerializerMethodField)

    def test_serializer_has_num_samplelibs_field(self):
        """Test serializer has num_samplelibs IntegerField"""
        from areas.serializers import AreasSerializer

        serializer = AreasSerializer()
        assert 'num_samplelibs' in serializer.fields
        assert isinstance(serializer.fields['num_samplelibs'], serializers.IntegerField)

    def test_serializer_has_completion_date_method_field(self):
        """Test serializer has completion_date SerializerMethodField"""
        from areas.serializers import AreasSerializer

        serializer = AreasSerializer()
        assert 'completion_date' in serializer.fields
        assert isinstance(serializer.fields['completion_date'], serializers.SerializerMethodField)

    def test_serializer_has_area_type_label_method_field(self):
        """Test serializer has area_type_label SerializerMethodField"""
        from areas.serializers import AreasSerializer

        serializer = AreasSerializer()
        assert 'area_type_label' in serializer.fields
        assert isinstance(serializer.fields['area_type_label'], serializers.SerializerMethodField)

    def test_get_dt_row_id_returns_object_id(self):
        """Test get_DT_RowId returns object id"""
        from areas.serializers import AreasSerializer

        # Mock area object
        mock_area = Mock()
        mock_area.id = 42

        serializer = AreasSerializer()
        result = serializer.get_DT_RowId(mock_area)

        assert result == 42

    def test_get_investigator_with_single_project(self):
        """Test get_investigator returns pi from project"""
        from areas.serializers import AreasSerializer

        # Mock project
        mock_project = Mock()
        mock_project.pi = 'Dr. Smith'

        # Mock block with projects
        mock_block = Mock()
        mock_block.block_projects.all.return_value = [mock_project]

        # Mock area with block
        mock_area = Mock()
        mock_area.block = mock_block

        serializer = AreasSerializer()
        result = serializer.get_investigator(mock_area)

        assert result == 'Dr. Smith'

    def test_get_investigator_with_multiple_projects(self):
        """Test get_investigator returns comma-separated pis"""
        from areas.serializers import AreasSerializer

        # Mock projects
        mock_project1 = Mock()
        mock_project1.pi = 'Dr. Smith'
        mock_project2 = Mock()
        mock_project2.pi = 'Dr. Jones'

        # Mock block with projects
        mock_block = Mock()
        mock_block.block_projects.all.return_value = [mock_project1, mock_project2]

        # Mock area with block
        mock_area = Mock()
        mock_area.block = mock_block

        serializer = AreasSerializer()
        result = serializer.get_investigator(mock_area)

        assert result == 'Dr. Smith, Dr. Jones'

    def test_get_investigator_with_no_projects(self):
        """Test get_investigator returns empty string when no projects"""
        from areas.serializers import AreasSerializer

        # Mock block with no projects
        mock_block = Mock()
        mock_block.block_projects.all.return_value = []

        # Mock area with block
        mock_area = Mock()
        mock_area.block = mock_block

        serializer = AreasSerializer()
        result = serializer.get_investigator(mock_area)

        assert result == ''

    def test_get_block_name_with_block(self):
        """Test get_block_name returns block name when block exists"""
        from areas.serializers import AreasSerializer

        # Mock block
        mock_block = Mock()
        mock_block.name = 'BLK001'

        # Mock area with block
        mock_area = Mock()
        mock_area.block = mock_block

        serializer = AreasSerializer()
        result = serializer.get_block_name(mock_area)

        assert result == 'BLK001'

    def test_get_block_name_without_block(self):
        """Test get_block_name returns None when block is None"""
        from areas.serializers import AreasSerializer

        # Mock area without block
        mock_area = Mock()
        mock_area.block = None

        serializer = AreasSerializer()
        result = serializer.get_block_name(mock_area)

        assert result is None

    def test_get_block_id_with_block(self):
        """Test get_block_id returns block id when block exists"""
        from areas.serializers import AreasSerializer

        # Mock block
        mock_block = Mock()
        mock_block.id = 123

        # Mock area with block
        mock_area = Mock()
        mock_area.block = mock_block

        serializer = AreasSerializer()
        result = serializer.get_block_id(mock_area)

        assert result == 123

    def test_get_block_id_without_block(self):
        """Test get_block_id returns None when block is None"""
        from areas.serializers import AreasSerializer

        # Mock area without block
        mock_area = Mock()
        mock_area.block = None

        serializer = AreasSerializer()
        result = serializer.get_block_id(mock_area)

        assert result is None

    def test_get_completion_date_returns_empty_string(self):
        """Test get_completion_date returns empty string"""
        from areas.serializers import AreasSerializer

        mock_area = Mock()

        serializer = AreasSerializer()
        result = serializer.get_completion_date(mock_area)

        assert result == ""

    def test_get_area_type_label_with_area_type(self):
        """Test get_area_type_label returns name when area_type exists"""
        from areas.serializers import AreasSerializer

        # Mock area_type
        mock_area_type = Mock()
        mock_area_type.name = 'Type A'

        # Mock area with area_type
        mock_area = Mock()
        mock_area.area_type = mock_area_type

        serializer = AreasSerializer()
        result = serializer.get_area_type_label(mock_area)

        assert result == 'Type A'

    def test_get_area_type_label_without_area_type(self):
        """Test get_area_type_label returns None when area_type is None"""
        from areas.serializers import AreasSerializer

        # Mock area without area_type
        mock_area = Mock()
        mock_area.area_type = None

        serializer = AreasSerializer()
        result = serializer.get_area_type_label(mock_area)

        assert result is None
