# tests/unit/blocks/test_serializers.py
"""
Blocks Serializers Test Cases - No Database Required
"""
import pytest
from unittest.mock import Mock, MagicMock
from rest_framework import serializers
from tests.utils.base_test import BaseAPITestNoDatabase
from tests.fixtures.blocks_fixtures import BlocksTestData


class TestBlocksSerializer(BaseAPITestNoDatabase):
    """Test BlocksSerializer"""

    def test_serializer_initialization(self):
        """Test BlocksSerializer initializes correctly"""
        from blocks.serializers import BlocksSerializer

        serializer = BlocksSerializer()
        assert serializer is not None

    def test_serializer_inherits_from_model_serializer(self):
        """Test BlocksSerializer inherits from ModelSerializer"""
        from blocks.serializers import BlocksSerializer

        assert issubclass(BlocksSerializer, serializers.ModelSerializer)

    def test_serializer_meta_model(self):
        """Test serializer Meta.model is Block"""
        from blocks.serializers import BlocksSerializer
        from blocks.models import Block

        assert BlocksSerializer.Meta.model == Block

    def test_serializer_meta_fields(self):
        """Test serializer Meta.fields includes expected fields"""
        from blocks.serializers import BlocksSerializer

        expected_fields = (
            "id", "name", "patient_id", "project", "patient", "diagnosis",
            "body_site", "thickness", "date_added", "num_areas", "DT_RowId",
            "block_url", "scan_number", "num_variants"
        )
        assert BlocksSerializer.Meta.fields == expected_fields

    def test_serializer_has_num_areas_field(self):
        """Test serializer has num_areas IntegerField"""
        from blocks.serializers import BlocksSerializer

        serializer = BlocksSerializer()
        assert 'num_areas' in serializer.fields
        assert isinstance(serializer.fields['num_areas'], serializers.IntegerField)

    def test_serializer_has_num_variants_field(self):
        """Test serializer has num_variants CharField"""
        from blocks.serializers import BlocksSerializer

        serializer = BlocksSerializer()
        assert 'num_variants' in serializer.fields
        assert isinstance(serializer.fields['num_variants'], serializers.CharField)

    def test_serializer_has_patient_id_method_field(self):
        """Test serializer has patient_id SerializerMethodField"""
        from blocks.serializers import BlocksSerializer

        serializer = BlocksSerializer()
        assert 'patient_id' in serializer.fields
        assert isinstance(serializer.fields['patient_id'], serializers.SerializerMethodField)

    def test_serializer_has_dt_row_id_method_field(self):
        """Test serializer has DT_RowId SerializerMethodField"""
        from blocks.serializers import BlocksSerializer

        serializer = BlocksSerializer()
        assert 'DT_RowId' in serializer.fields
        assert isinstance(serializer.fields['DT_RowId'], serializers.SerializerMethodField)

    def test_serializer_has_body_site_method_field(self):
        """Test serializer has body_site SerializerMethodField"""
        from blocks.serializers import BlocksSerializer

        serializer = BlocksSerializer()
        assert 'body_site' in serializer.fields
        assert isinstance(serializer.fields['body_site'], serializers.SerializerMethodField)

    def test_serializer_has_patient_method_field(self):
        """Test serializer has patient SerializerMethodField"""
        from blocks.serializers import BlocksSerializer

        serializer = BlocksSerializer()
        assert 'patient' in serializer.fields
        assert isinstance(serializer.fields['patient'], serializers.SerializerMethodField)

    def test_serializer_has_project_method_field(self):
        """Test serializer has project SerializerMethodField"""
        from blocks.serializers import BlocksSerializer

        serializer = BlocksSerializer()
        assert 'project' in serializer.fields
        assert isinstance(serializer.fields['project'], serializers.SerializerMethodField)

    def test_get_dt_row_id_returns_object_id(self):
        """Test get_DT_RowId returns object id"""
        from blocks.serializers import BlocksSerializer

        # Mock block object
        mock_block = Mock()
        mock_block.id = 42

        serializer = BlocksSerializer()
        result = serializer.get_DT_RowId(mock_block)

        assert result == 42

    def test_get_patient_with_patient(self):
        """Test get_patient returns pat_id when patient exists"""
        from blocks.serializers import BlocksSerializer

        # Mock patient
        mock_patient = Mock()
        mock_patient.pat_id = 'PAT123'

        # Mock block with patient
        mock_block = Mock()
        mock_block.patient = mock_patient

        serializer = BlocksSerializer()
        result = serializer.get_patient(mock_block)

        assert result == 'PAT123'

    def test_get_patient_without_patient(self):
        """Test get_patient returns None when patient is None"""
        from blocks.serializers import BlocksSerializer

        # Mock block without patient
        mock_block = Mock()
        mock_block.patient = None

        serializer = BlocksSerializer()
        result = serializer.get_patient(mock_block)

        assert result is None

    def test_get_body_site_with_body_site(self):
        """Test get_body_site returns name when body_site exists"""
        from blocks.serializers import BlocksSerializer

        # Mock body site
        mock_body_site = Mock()
        mock_body_site.name = 'Arm'

        # Mock block with body_site
        mock_block = Mock()
        mock_block.body_site = mock_body_site

        serializer = BlocksSerializer()
        result = serializer.get_body_site(mock_block)

        assert result == 'Arm'

    def test_get_body_site_without_body_site(self):
        """Test get_body_site returns None when body_site is None"""
        from blocks.serializers import BlocksSerializer

        # Mock block without body_site
        mock_block = Mock()
        mock_block.body_site = None

        serializer = BlocksSerializer()
        result = serializer.get_body_site(mock_block)

        assert result is None

    def test_get_patient_id_with_patient(self):
        """Test get_patient_id returns patient id when patient exists"""
        from blocks.serializers import BlocksSerializer

        # Mock patient
        mock_patient = Mock()
        mock_patient.id = 123

        # Mock block with patient
        mock_block = Mock()
        mock_block.patient = mock_patient

        serializer = BlocksSerializer()
        result = serializer.get_patient_id(mock_block)

        assert result == 123

    def test_get_patient_id_without_patient(self):
        """Test get_patient_id returns None when patient is None"""
        from blocks.serializers import BlocksSerializer

        # Mock block without patient
        mock_block = Mock()
        mock_block.patient = None

        serializer = BlocksSerializer()
        result = serializer.get_patient_id(mock_block)

        assert result is None

    def test_get_project_with_single_project(self):
        """Test get_project returns project abbreviation"""
        from blocks.serializers import BlocksSerializer

        # Mock project
        mock_project = Mock()
        mock_project.abbreviation = 'PROJ1'

        # Mock block with projects
        mock_block = Mock()
        mock_block.block_projects.all.return_value = [mock_project]

        serializer = BlocksSerializer()
        result = serializer.get_project(mock_block)

        assert result == 'PROJ1'

    def test_get_project_with_multiple_projects(self):
        """Test get_project returns comma-separated abbreviations"""
        from blocks.serializers import BlocksSerializer

        # Mock projects
        mock_project1 = Mock()
        mock_project1.abbreviation = 'PROJ1'
        mock_project2 = Mock()
        mock_project2.abbreviation = 'PROJ2'

        # Mock block with multiple projects
        mock_block = Mock()
        mock_block.block_projects.all.return_value = [mock_project1, mock_project2]

        serializer = BlocksSerializer()
        result = serializer.get_project(mock_block)

        assert result == 'PROJ1, PROJ2'

    def test_get_project_with_no_projects(self):
        """Test get_project returns empty string when no projects"""
        from blocks.serializers import BlocksSerializer

        # Mock block with no projects
        mock_block = Mock()
        mock_block.block_projects.all.return_value = []

        serializer = BlocksSerializer()
        result = serializer.get_project(mock_block)

        assert result == ''

    def test_block_url_field_allows_null(self):
        """Test block_url field allows null"""
        from blocks.serializers import BlocksSerializer

        serializer = BlocksSerializer()
        assert serializer.fields['block_url'].allow_null is True

    def test_block_url_field_not_required(self):
        """Test block_url field is not required"""
        from blocks.serializers import BlocksSerializer

        serializer = BlocksSerializer()
        assert serializer.fields['block_url'].required is False


class TestSingleBlockSerializer(BaseAPITestNoDatabase):
    """Test SingleBlockSerializer"""

    def test_serializer_initialization(self):
        """Test SingleBlockSerializer initializes correctly"""
        from blocks.serializers import SingleBlockSerializer

        serializer = SingleBlockSerializer()
        assert serializer is not None

    def test_serializer_inherits_from_model_serializer(self):
        """Test SingleBlockSerializer inherits from ModelSerializer"""
        from blocks.serializers import SingleBlockSerializer

        assert issubclass(SingleBlockSerializer, serializers.ModelSerializer)

    def test_serializer_meta_model(self):
        """Test serializer Meta.model is Block"""
        from blocks.serializers import SingleBlockSerializer
        from blocks.models import Block

        assert SingleBlockSerializer.Meta.model == Block

    def test_serializer_meta_fields_all(self):
        """Test serializer Meta.fields is __all__"""
        from blocks.serializers import SingleBlockSerializer

        assert SingleBlockSerializer.Meta.fields == "__all__"

    def test_serializer_has_patient_method_field(self):
        """Test serializer has patient SerializerMethodField"""
        from blocks.serializers import SingleBlockSerializer

        serializer = SingleBlockSerializer()
        assert 'patient' in serializer.fields
        assert isinstance(serializer.fields['patient'], serializers.SerializerMethodField)

    def test_serializer_has_project_method_field(self):
        """Test serializer has project SerializerMethodField"""
        from blocks.serializers import SingleBlockSerializer

        serializer = SingleBlockSerializer()
        assert 'project' in serializer.fields
        assert isinstance(serializer.fields['project'], serializers.SerializerMethodField)

    def test_get_patient_with_patient(self):
        """Test get_patient returns pat_id when patient exists"""
        from blocks.serializers import SingleBlockSerializer

        # Mock patient
        mock_patient = Mock()
        mock_patient.pat_id = 'PAT456'

        # Mock block with patient
        mock_block = Mock()
        mock_block.patient = mock_patient

        serializer = SingleBlockSerializer()
        result = serializer.get_patient(mock_block)

        assert result == 'PAT456'

    def test_get_patient_without_patient(self):
        """Test get_patient returns None when patient is None"""
        from blocks.serializers import SingleBlockSerializer

        # Mock block without patient
        mock_block = Mock()
        mock_block.patient = None

        serializer = SingleBlockSerializer()
        result = serializer.get_patient(mock_block)

        assert result is None

    def test_get_project_with_single_project(self):
        """Test get_project returns project name"""
        from blocks.serializers import SingleBlockSerializer

        # Mock project
        mock_project = Mock()
        mock_project.name = 'Project Alpha'

        # Mock block with projects
        mock_block = Mock()
        mock_block.block_projects.all.return_value = [mock_project]

        serializer = SingleBlockSerializer()
        result = serializer.get_project(mock_block)

        assert result == 'Project Alpha'

    def test_get_project_with_multiple_projects(self):
        """Test get_project returns comma-separated project names"""
        from blocks.serializers import SingleBlockSerializer

        # Mock projects
        mock_project1 = Mock()
        mock_project1.name = 'Project Alpha'
        mock_project2 = Mock()
        mock_project2.name = 'Project Beta'

        # Mock block with multiple projects
        mock_block = Mock()
        mock_block.block_projects.all.return_value = [mock_project1, mock_project2]

        serializer = SingleBlockSerializer()
        result = serializer.get_project(mock_block)

        assert result == 'Project Alpha, Project Beta'

    def test_get_project_with_no_projects(self):
        """Test get_project returns empty string when no projects"""
        from blocks.serializers import SingleBlockSerializer

        # Mock block with no projects
        mock_block = Mock()
        mock_block.block_projects.all.return_value = []

        serializer = SingleBlockSerializer()
        result = serializer.get_project(mock_block)

        assert result == ''


class TestSerializerComparison(BaseAPITestNoDatabase):
    """Test comparison between BlocksSerializer and SingleBlockSerializer"""

    def test_both_use_same_model(self):
        """Test both serializers use Block model"""
        from blocks.serializers import BlocksSerializer, SingleBlockSerializer

        assert BlocksSerializer.Meta.model == SingleBlockSerializer.Meta.model

    def test_blocks_serializer_uses_abbreviation_single_uses_name(self):
        """Test BlocksSerializer uses abbreviation, SingleBlockSerializer uses name"""
        from blocks.serializers import BlocksSerializer, SingleBlockSerializer

        # Mock project
        mock_project = Mock()
        mock_project.abbreviation = 'PROJ1'
        mock_project.name = 'Project One'

        # Mock block
        mock_block = Mock()
        mock_block.block_projects.all.return_value = [mock_project]

        blocks_serializer = BlocksSerializer()
        single_serializer = SingleBlockSerializer()

        blocks_result = blocks_serializer.get_project(mock_block)
        single_result = single_serializer.get_project(mock_block)

        assert blocks_result == 'PROJ1'
        assert single_result == 'Project One'

    def test_blocks_serializer_limited_fields_single_all_fields(self):
        """Test BlocksSerializer has specific fields, SingleBlockSerializer has all"""
        from blocks.serializers import BlocksSerializer, SingleBlockSerializer

        assert isinstance(BlocksSerializer.Meta.fields, tuple)
        assert SingleBlockSerializer.Meta.fields == "__all__"
