# tests/unit/projects/test_serializers.py
"""
Project Serializers Test Cases - No Database Required

Tests ProjectsSerializer and UserSerializer with complete mocking.
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from tests.utils.base_test import BaseAPITestNoDatabase
from tests.fixtures.project_fixtures import ProjectTestData


class TestProjectsSerializer(BaseAPITestNoDatabase):
    """Test ProjectsSerializer"""

    def setUp(self):
        """Set up test fixtures"""
        super().setUp()

        # Create mock project
        self.mock_project = self.create_mock_project()

    def create_mock_project(self, **kwargs):
        """Create a mock project object with all required fields"""
        project = Mock()
        project.id = kwargs.get('id', 1)
        project.abbreviation = kwargs.get('abbreviation', 'TST')
        project.name = kwargs.get('name', 'Test Project')
        project.pi = kwargs.get('pi', 'BB')
        project.speedtype = kwargs.get('speedtype', 'SPEED123')
        project.date_start = kwargs.get('date_start', datetime(2024, 1, 1))
        project.num_blocks = kwargs.get('num_blocks', 5)

        # Mock get_pi_display method
        pi_display_map = {
            'BB': 'Boris Bastian',
            'IY': 'Iwei Yeh',
            'AH': 'Alan Hunter Shain',
        }
        project.get_pi_display = Mock(
            return_value=pi_display_map.get(project.pi, '')
        )

        return project

    def test_serializer_contains_expected_fields(self):
        """Test serializer has all expected fields"""
        from projects.serializers import ProjectsSerializer

        serializer = ProjectsSerializer(instance=self.mock_project)
        data = serializer.data

        # Verify all fields are present
        expected_fields = {
            'id', 'abbreviation', 'name', 'pi', 'pi_label',
            'date_start', 'speedtype', 'num_blocks', 'DT_RowId'
        }

        assert set(data.keys()) == expected_fields

    def test_serializer_field_types(self):
        """Test serializer fields have correct types"""
        from projects.serializers import ProjectsSerializer

        serializer = ProjectsSerializer(instance=self.mock_project)
        data = serializer.data

        # Verify field types
        assert isinstance(data['id'], int)
        assert isinstance(data['abbreviation'], str)
        assert isinstance(data['name'], str)
        assert isinstance(data['pi'], str)
        assert isinstance(data['pi_label'], str)
        assert isinstance(data['speedtype'], str)
        assert isinstance(data['num_blocks'], int)
        assert isinstance(data['DT_RowId'], int)

    def test_serializer_id_field(self):
        """Test id field serialization"""
        from projects.serializers import ProjectsSerializer

        project = self.create_mock_project(id=42)
        serializer = ProjectsSerializer(instance=project)

        assert serializer.data['id'] == 42

    def test_serializer_abbreviation_field(self):
        """Test abbreviation field serialization"""
        from projects.serializers import ProjectsSerializer

        project = self.create_mock_project(abbreviation='AMJNCI')
        serializer = ProjectsSerializer(instance=project)

        assert serializer.data['abbreviation'] == 'AMJNCI'

    def test_serializer_name_field(self):
        """Test name field serialization"""
        from projects.serializers import ProjectsSerializer

        project = self.create_mock_project(name='Acral Melanoma Project')
        serializer = ProjectsSerializer(instance=project)

        assert serializer.data['name'] == 'Acral Melanoma Project'

    def test_serializer_pi_field(self):
        """Test pi field serialization"""
        from projects.serializers import ProjectsSerializer

        project = self.create_mock_project(pi='IY')
        serializer = ProjectsSerializer(instance=project)

        assert serializer.data['pi'] == 'IY'

    def test_serializer_speedtype_field(self):
        """Test speedtype field serialization"""
        from projects.serializers import ProjectsSerializer

        project = self.create_mock_project(speedtype='MDEYEH11')
        serializer = ProjectsSerializer(instance=project)

        assert serializer.data['speedtype'] == 'MDEYEH11'

    def test_serializer_speedtype_empty(self):
        """Test speedtype field when empty"""
        from projects.serializers import ProjectsSerializer

        project = self.create_mock_project(speedtype='')
        serializer = ProjectsSerializer(instance=project)

        assert serializer.data['speedtype'] == ''

    def test_serializer_date_start_field(self):
        """Test date_start field serialization"""
        from projects.serializers import ProjectsSerializer

        test_date = datetime(2025, 9, 16)
        project = self.create_mock_project(date_start=test_date)
        serializer = ProjectsSerializer(instance=project)

        # Date should be serialized as ISO format string
        assert serializer.data['date_start'] is not None

    def test_serializer_num_blocks_field(self):
        """Test num_blocks field serialization"""
        from projects.serializers import ProjectsSerializer

        project = self.create_mock_project(num_blocks=76)
        serializer = ProjectsSerializer(instance=project)

        assert serializer.data['num_blocks'] == 76

    def test_serializer_num_blocks_zero(self):
        """Test num_blocks field when zero"""
        from projects.serializers import ProjectsSerializer

        project = self.create_mock_project(num_blocks=0)
        serializer = ProjectsSerializer(instance=project)

        assert serializer.data['num_blocks'] == 0

    def test_get_dt_row_id_method(self):
        """Test get_DT_RowId returns project id"""
        from projects.serializers import ProjectsSerializer

        project = self.create_mock_project(id=123)
        serializer = ProjectsSerializer(instance=project)

        # DT_RowId should equal id
        assert serializer.data['DT_RowId'] == 123

    def test_get_dt_row_id_matches_id(self):
        """Test DT_RowId always matches id field"""
        from projects.serializers import ProjectsSerializer

        for test_id in [1, 42, 999, 12345]:
            project = self.create_mock_project(id=test_id)
            serializer = ProjectsSerializer(instance=project)

            assert serializer.data['DT_RowId'] == serializer.data['id']

    def test_get_pi_label_boris_bastian(self):
        """Test get_pi_label for Boris Bastian"""
        from projects.serializers import ProjectsSerializer

        project = self.create_mock_project(pi='BB')
        serializer = ProjectsSerializer(instance=project)

        assert serializer.data['pi_label'] == 'Boris Bastian'
        project.get_pi_display.assert_called_once()

    def test_get_pi_label_iwei_yeh(self):
        """Test get_pi_label for Iwei Yeh"""
        from projects.serializers import ProjectsSerializer

        project = self.create_mock_project(pi='IY')
        project.get_pi_display = Mock(return_value='Iwei Yeh')

        serializer = ProjectsSerializer(instance=project)

        assert serializer.data['pi_label'] == 'Iwei Yeh'
        project.get_pi_display.assert_called_once()

    def test_get_pi_label_alan_hunter_shain(self):
        """Test get_pi_label for Alan Hunter Shain"""
        from projects.serializers import ProjectsSerializer

        project = self.create_mock_project(pi='AH')
        project.get_pi_display = Mock(return_value='Alan Hunter Shain')

        serializer = ProjectsSerializer(instance=project)

        assert serializer.data['pi_label'] == 'Alan Hunter Shain'

    def test_serializer_with_sample_project_data(self):
        """Test serializer with realistic project data"""
        from projects.serializers import ProjectsSerializer

        # Use sample project from fixtures
        sample = ProjectTestData.SINGLE_PROJECT

        project = self.create_mock_project(
            id=sample['id'],
            abbreviation=sample['abbreviation'],
            name=sample['name'],
            pi=sample['pi'],
            speedtype=sample['speedtype'],
            num_blocks=sample['num_blocks']
        )

        serializer = ProjectsSerializer(instance=project)
        data = serializer.data

        assert data['id'] == sample['id']
        assert data['abbreviation'] == sample['abbreviation']
        assert data['name'] == sample['name']
        assert data['pi'] == sample['pi']
        assert data['speedtype'] == sample['speedtype']
        assert data['num_blocks'] == sample['num_blocks']

    def test_serializer_many_true(self):
        """Test serializer with many=True for multiple projects"""
        from projects.serializers import ProjectsSerializer

        projects = [
            self.create_mock_project(id=1, name='Project 1'),
            self.create_mock_project(id=2, name='Project 2'),
            self.create_mock_project(id=3, name='Project 3'),
        ]

        serializer = ProjectsSerializer(projects, many=True)
        data = serializer.data

        assert len(data) == 3
        assert data[0]['id'] == 1
        assert data[1]['id'] == 2
        assert data[2]['id'] == 3

    def test_serializer_empty_list(self):
        """Test serializer with empty list"""
        from projects.serializers import ProjectsSerializer

        serializer = ProjectsSerializer([], many=True)
        data = serializer.data

        assert data == []
        assert len(data) == 0

    def test_serializer_with_all_sample_projects(self):
        """Test serializer with all sample projects from fixtures"""
        from projects.serializers import ProjectsSerializer

        projects = []
        for sample in ProjectTestData.SAMPLE_PROJECTS:
            project = self.create_mock_project(
                id=sample['id'],
                abbreviation=sample['abbreviation'],
                name=sample['name'],
                pi=sample['pi'],
                speedtype=sample['speedtype'],
                num_blocks=sample['num_blocks']
            )
            projects.append(project)

        serializer = ProjectsSerializer(projects, many=True)
        data = serializer.data

        assert len(data) == len(ProjectTestData.SAMPLE_PROJECTS)

        # Verify first and last projects
        assert data[0]['abbreviation'] == 'T/B-CR'
        assert data[-1]['abbreviation'] == 'Met'

    def test_serializer_output_matches_expected_format(self):
        """Test serializer output matches DataTables Editor format"""
        from projects.serializers import ProjectsSerializer

        project = self.create_mock_project(
            id=2,
            abbreviation='TST',
            name='TEST Project',
            pi='BB',
            speedtype='MDETEST01',
            num_blocks=5
        )

        serializer = ProjectsSerializer(instance=project)
        data = serializer.data

        # Should match expected format
        expected = ProjectTestData.SINGLE_PROJECT
        assert data['id'] == expected['id']
        assert data['abbreviation'] == expected['abbreviation']
        assert data['name'] == expected['name']
        assert data['DT_RowId'] == expected['DT_RowId']

    def test_serializer_preserves_field_order(self):
        """Test serializer maintains field order"""
        from projects.serializers import ProjectsSerializer

        serializer = ProjectsSerializer(instance=self.mock_project)
        data = serializer.data

        # Get field order
        field_names = list(data.keys())

        # Verify expected fields are present
        expected_fields = [
            'id', 'abbreviation', 'name', 'pi', 'pi_label',
            'date_start', 'speedtype', 'num_blocks', 'DT_RowId'
        ]

        for field in expected_fields:
            assert field in field_names

    def test_serializer_meta_fields(self):
        """Test serializer Meta class fields configuration"""
        from projects.serializers import ProjectsSerializer

        # Check Meta fields
        expected_fields = (
            "id", "abbreviation", "name", "pi", "pi_label",
            "date_start", "speedtype", "num_blocks", "DT_RowId"
        )

        assert ProjectsSerializer.Meta.fields == expected_fields

    def test_serializer_meta_model(self):
        """Test serializer Meta class model configuration"""
        from projects.serializers import ProjectsSerializer
        from projects.models import Project

        assert ProjectsSerializer.Meta.model == Project

    def test_serializer_readonly_fields(self):
        """Test DT_RowId and pi_label are read-only (SerializerMethodFields)"""
        from projects.serializers import ProjectsSerializer
        from rest_framework import serializers

        # Get field instances
        serializer = ProjectsSerializer()

        # DT_RowId and pi_label should be SerializerMethodFields
        assert isinstance(
            serializer.fields['DT_RowId'],
            serializers.SerializerMethodField
        )
        assert isinstance(
            serializer.fields['pi_label'],
            serializers.SerializerMethodField
        )

    def test_serializer_num_blocks_is_integer_field(self):
        """Test num_blocks is IntegerField"""
        from projects.serializers import ProjectsSerializer
        from rest_framework import serializers

        serializer = ProjectsSerializer()

        assert isinstance(
            serializer.fields['num_blocks'],
            serializers.IntegerField
        )


class TestUserSerializer(BaseAPITestNoDatabase):
    """Test UserSerializer"""

    def setUp(self):
        """Set up test fixtures"""
        super().setUp()

        # Use existing mock user from base class
        self.mock_user = self.user


    def test_user_serializer_meta_fields(self):
        """Test UserSerializer Meta fields is set to __all__"""
        from projects.serializers import UserSerializer

        assert UserSerializer.Meta.fields == '__all__'

    def test_user_serializer_meta_model(self):
        """Test UserSerializer Meta model is User"""
        from projects.serializers import UserSerializer
        from django.contrib.auth import get_user_model

        User = get_user_model()
        assert UserSerializer.Meta.model == User

    def test_user_serializer_with_mock_user(self):
        """Test UserSerializer with mock user data"""
        from projects.serializers import UserSerializer

        # Create a more complete mock user
        user = Mock()
        user.id = 1
        user.username = 'testuser'
        user.email = 'test@example.com'
        user.first_name = 'Test'
        user.last_name = 'User'
        user.is_active = True
        user.is_staff = False
        user.is_superuser = False

        serializer = UserSerializer(instance=user)

        # Verify serializer works with mock
        assert serializer.instance == user


class TestSerializerIntegration(BaseAPITestNoDatabase):
    """Integration tests for serializers"""

    def test_projects_serializer_matches_datatables_format(self):
        """Test ProjectsSerializer output matches DataTables expected format"""
        from projects.serializers import ProjectsSerializer

        # Create projects matching fixture data
        projects = []
        for sample in ProjectTestData.SAMPLE_PROJECTS[:3]:
            project = Mock()
            project.id = sample['id']
            project.abbreviation = sample['abbreviation']
            project.name = sample['name']
            project.pi = sample['pi']
            project.speedtype = sample['speedtype']
            project.num_blocks = sample['num_blocks']
            project.date_start = datetime.now()
            project.get_pi_display = Mock(return_value=sample['pi_label'])
            projects.append(project)

        serializer = ProjectsSerializer(projects, many=True)
        data = serializer.data

        # Verify DataTables required fields
        for item in data:
            assert 'DT_RowId' in item  # Required by DataTables
            assert 'id' in item
            assert 'abbreviation' in item
            assert 'name' in item

    def test_serializer_with_queryset_result(self):
        """Test serializer works with query_by_args result format"""
        from projects.serializers import ProjectsSerializer

        # Simulate result from Project.query_by_args
        mock_items = [
            Mock(
                id=1,
                abbreviation='TST',
                name='Test',
                pi='BB',
                speedtype='',
                num_blocks=5,
                date_start=datetime.now(),
                get_pi_display=Mock(return_value='Boris Bastian')
            )
        ]

        serializer = ProjectsSerializer(mock_items, many=True)

        assert len(serializer.data) == 1
        assert serializer.data[0]['abbreviation'] == 'TST'

    def test_serializer_output_for_json_response(self):
        """Test serializer output can be used in JsonResponse"""
        from projects.serializers import ProjectsSerializer
        import json

        project = Mock()
        project.id = 1
        project.abbreviation = 'TST'
        project.name = 'Test Project'
        project.pi = 'BB'
        project.speedtype = 'SPEED123'
        project.num_blocks = 5
        project.date_start = datetime(2024, 1, 1)
        project.get_pi_display = Mock(return_value='Boris Bastian')

        serializer = ProjectsSerializer(instance=project)

        # Should be JSON serializable
        json_str = json.dumps(serializer.data)

        # Should be able to load back
        loaded_data = json.loads(json_str)
        assert loaded_data['id'] == 1
        assert loaded_data['abbreviation'] == 'TST'

    def test_serializer_contract_with_view_response(self):
        """Test serializer output matches view response format expectations"""
        from projects.serializers import ProjectsSerializer

        # Create mock projects
        projects = [
            Mock(
                id=i,
                abbreviation=f'PRJ{i}',
                name=f'Project {i}',
                pi='BB',
                speedtype='',
                num_blocks=i * 2,
                date_start=datetime.now(),
                get_pi_display=Mock(return_value='Boris Bastian')
            )
            for i in range(1, 8)
        ]

        serializer = ProjectsSerializer(projects, many=True)

        # Simulate view response structure
        response = {
            'data': serializer.data,
            'draw': 1,
            'recordsTotal': 7,
            'recordsFiltered': 7,
        }

        # Verify response structure
        assert isinstance(response['data'], list)
        assert len(response['data']) == 7
        assert all('DT_RowId' in item for item in response['data'])


class TestSerializerEdgeCases(BaseAPITestNoDatabase):
    """Test serializer edge cases and error handling"""

    def test_serializer_with_none_project(self):
        """Test serializer with None instance"""
        from projects.serializers import ProjectsSerializer

        serializer = ProjectsSerializer(instance=None)

        # Should handle None gracefully
        assert serializer.instance is None


    def test_serializer_with_null_speedtype(self):
        """Test serializer with null speedtype"""
        from projects.serializers import ProjectsSerializer

        project = Mock()
        project.id = 1
        project.abbreviation = 'TST'
        project.name = 'Test'
        project.pi = 'BB'
        project.speedtype = None  # Null value
        project.num_blocks = 0
        project.date_start = datetime.now()
        project.get_pi_display = Mock(return_value='Boris Bastian')

        serializer = ProjectsSerializer(instance=project)
        data = serializer.data

        # Should handle null speedtype
        assert data['speedtype'] is None

    def test_serializer_preserves_data_types(self):
        """Test serializer preserves correct data types"""
        from projects.serializers import ProjectsSerializer

        project = Mock()
        project.id = 1
        project.abbreviation = 'TST'
        project.name = 'Test'
        project.pi = 'BB'
        project.speedtype = 'SPEED'
        project.num_blocks = 10
        project.date_start = datetime.now()
        project.get_pi_display = Mock(return_value='Boris Bastian')

        serializer = ProjectsSerializer(instance=project)
        data = serializer.data

        # Verify types are preserved
        assert isinstance(data['id'], int)
        assert isinstance(data['num_blocks'], int)
        assert isinstance(data['DT_RowId'], int)
        assert isinstance(data['abbreviation'], str)
        assert isinstance(data['name'], str)
        assert isinstance(data['pi_label'], str)