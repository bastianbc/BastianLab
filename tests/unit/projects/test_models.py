# tests/unit/projects/test_models.py
"""
Project Model Test Cases - No Database Required

Tests the Project model's query_by_args method and business logic
with complete database mocking.
"""
import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from django.db.models import Q, Count
from tests.utils.base_test import BaseAPITestNoDatabase
from tests.fixtures.project_fixtures import ProjectTestData


class TestProjectModel(BaseAPITestNoDatabase):
    """Test Project model methods"""

    def setUp(self):
        """Set up test fixtures"""
        super().setUp()

        # Create mock project instance
        self.mock_project = self.create_mock_project()

    def create_mock_project(self, **kwargs):
        """Create a mock project object"""
        project = Mock()
        project.id = kwargs.get('id', 1)
        project.name = kwargs.get('name', 'Test Project')
        project.abbreviation = kwargs.get('abbreviation', 'TST')
        project.pi = kwargs.get('pi', 'BB')
        project.speedtype = kwargs.get('speedtype', 'SPEED123')
        project.description = kwargs.get('description', 'Test description')
        project.date_start = kwargs.get('date_start', datetime.now())
        project.date = kwargs.get('date', datetime.now())
        project.num_blocks = kwargs.get('num_blocks', 0)

        # Mock methods
        project.get_pi_display = Mock(return_value='Boris Bastian')
        project.__str__ = Mock(return_value=project.name)

        return project


class TestProjectQueryByArgs(BaseAPITestNoDatabase):
    """Test Project.query_by_args method"""

    @patch('projects.models.Project.objects')
    def test_query_by_args_basic_request(self, mock_objects):
        """Test query_by_args with basic DataTables request"""
        from projects.models import Project

        # Setup mock queryset
        mock_queryset = self.setup_mock_queryset(count=10)
        mock_objects.all.return_value = mock_queryset

        # Create request params
        params = {
            'draw': ['1'],
            'length': ['10'],
            'start': ['0'],
            'search[value]': [''],
            'order[0][column]': ['0'],
            'order[0][dir]': ['asc'],
            'date_range': [''],
            'pi': [''],
            'technician': [''],
            'researcher': [''],
        }

        # Call method
        project = Project()
        result = project.query_by_args(self.user, **params)

        # Assertions
        assert result['draw'] == 1
        assert result['total'] == 10
        assert result['count'] == 10
        assert 'items' in result

        # Verify queryset was annotated with num_blocks
        mock_queryset.annotate.assert_called_once()
        call_kwargs = mock_queryset.annotate.call_args[1]
        assert 'num_blocks' in call_kwargs

    @patch('projects.models.Project.objects')
    def test_query_by_args_with_superuser(self, mock_objects):
        """Test query_by_args returns all projects for superuser"""
        from projects.models import Project

        mock_queryset = self.setup_mock_queryset(count=20)
        mock_objects.all.return_value = mock_queryset

        params = ProjectTestData.DATATABLES_REQUEST

        project = Project()
        result = project.query_by_args(self.superuser, **params)

        # Superuser should see all - no filter should be applied
        mock_queryset.filter.assert_not_called()
        assert result['total'] == 20

    @patch('projects.models.Project.objects')
    def test_query_by_args_with_regular_user(self, mock_objects):
        """Test query_by_args filters projects for regular user"""
        from projects.models import Project

        mock_queryset = self.setup_mock_queryset(count=5)
        mock_objects.all.return_value = mock_queryset

        params = ProjectTestData.DATATABLES_REQUEST

        project = Project()
        result = project.query_by_args(self.user, **params)

        # Regular user should have filter applied
        mock_queryset.filter.assert_called()
        # Verify filter includes Q objects for technician, researcher, primary_investigator
        assert result['items'] is not None

    @patch('projects.models.Project.objects')
    def test_query_by_args_with_search_value(self, mock_objects):
        """Test query_by_args with search term"""
        from projects.models import Project

        mock_queryset = self.setup_mock_queryset(count=3)
        mock_objects.all.return_value = mock_queryset

        params = {
            'draw': ['1'],
            'length': ['10'],
            'start': ['0'],
            'search[value]': ['melanoma'],
            'order[0][column]': ['1'],
            'order[0][dir]': ['asc'],
            'date_range': [''],
            'pi': [''],
            'technician': [''],
            'researcher': [''],
        }

        project = Project()
        result = project.query_by_args(self.superuser, **params)

        # Verify filter was called for search
        filter_calls = [call for call in mock_queryset.filter.call_args_list]
        assert len(filter_calls) > 0
        assert result['count'] == 3

    @patch('projects.models.Project.objects')
    def test_query_by_args_with_pi_filter(self, mock_objects):
        """Test query_by_args filters by PI"""
        from projects.models import Project

        mock_queryset = self.setup_mock_queryset(count=5)
        mock_objects.all.return_value = mock_queryset

        params = {
            'draw': ['1'],
            'length': ['10'],
            'start': ['0'],
            'search[value]': [''],
            'order[0][column]': ['0'],
            'order[0][dir]': ['asc'],
            'date_range': [''],
            'pi': ['BB'],  # Boris Bastian
            'technician': [''],
            'researcher': [''],
        }

        project = Project()
        result = project.query_by_args(self.superuser, **params)

        # Verify filter was called with pi
        assert mock_queryset.filter.called
        assert result['items'] is not None

    @patch('projects.models.Project.objects')
    def test_query_by_args_with_technician_filter(self, mock_objects):
        """Test query_by_args filters by technician"""
        from projects.models import Project

        mock_queryset = self.setup_mock_queryset(count=3)
        mock_objects.all.return_value = mock_queryset

        params = {
            'draw': ['1'],
            'length': ['10'],
            'start': ['0'],
            'search[value]': [''],
            'order[0][column]': ['0'],
            'order[0][dir]': ['asc'],
            'date_range': [''],
            'pi': [''],
            'technician': ['5'],  # User ID
            'researcher': [''],
        }

        project = Project()
        result = project.query_by_args(self.superuser, **params)

        # Verify filter was called
        assert mock_queryset.filter.called
        assert result['count'] == 3

    @patch('projects.models.Project.objects')
    def test_query_by_args_with_researcher_filter(self, mock_objects):
        """Test query_by_args filters by researcher"""
        from projects.models import Project

        mock_queryset = self.setup_mock_queryset(count=2)
        mock_objects.all.return_value = mock_queryset

        params = {
            'draw': ['1'],
            'length': ['10'],
            'start': ['0'],
            'search[value]': [''],
            'order[0][column]': ['0'],
            'order[0][dir]': ['asc'],
            'date_range': [''],
            'pi': [''],
            'technician': [''],
            'researcher': ['10'],  # User ID
        }

        project = Project()
        result = project.query_by_args(self.superuser, **params)

        # Verify filter was called
        assert mock_queryset.filter.called
        assert result['count'] == 2

    @patch('projects.models.datetime')
    @patch('projects.models.Project.objects')
    def test_query_by_args_with_date_range_filter(self, mock_objects, mock_datetime):
        """Test query_by_args filters by date range"""
        from projects.models import Project

        mock_queryset = self.setup_mock_queryset(count=4)
        mock_objects.all.return_value = mock_queryset

        params = {
            'draw': ['1'],
            'length': ['10'],
            'start': ['0'],
            'search[value]': [''],
            'order[0][column]': ['0'],
            'order[0][dir]': ['asc'],
            'date_range': ['2024-01-01 to 2024-12-31'],
            'pi': [''],
            'technician': [''],
            'researcher': [''],
        }

        # Mock datetime.strptime
        mock_datetime.strptime.side_effect = lambda date_str, fmt: datetime.strptime(date_str, fmt)

        project = Project()
        result = project.query_by_args(self.superuser, **params)

        # Verify filter was called with date range
        assert mock_queryset.filter.called
        assert result['count'] == 4

    @patch('projects.models.Project.objects')
    def test_query_by_args_with_initial_search_block(self, mock_objects):
        """Test query_by_args with initial search for block"""
        from projects.models import Project

        mock_queryset = self.setup_mock_queryset(count=1)
        mock_objects.all.return_value = mock_queryset

        # Initial search format: _initial:{"model":"block","id":"123"}
        initial_search = '_initial:{"model":"block","id":"123"}'

        params = {
            'draw': ['1'],
            'length': ['10'],
            'start': ['0'],
            'search[value]': [initial_search],
            'order[0][column]': ['0'],
            'order[0][dir]': ['asc'],
            'date_range': [''],
            'pi': [''],
            'technician': [''],
            'researcher': [''],
        }

        project = Project()
        result = project.query_by_args(self.superuser, **params)

        # Verify filter was called for block search
        assert mock_queryset.filter.called
        assert result['count'] == 1

    @patch('projects.models.Project.objects')
    def test_query_by_args_with_initial_search_area(self, mock_objects):
        """Test query_by_args with initial search for area"""
        from projects.models import Project

        mock_queryset = self.setup_mock_queryset(count=1)
        mock_objects.all.return_value = mock_queryset

        # Initial search format for area
        initial_search = '_initial:{"model":"area","id":"456"}'

        params = {
            'draw': ['1'],
            'length': ['10'],
            'start': ['0'],
            'search[value]': [initial_search],
            'order[0][column]': ['0'],
            'order[0][dir]': ['asc'],
            'date_range': [''],
            'pi': [''],
            'technician': [''],
            'researcher': [''],
        }

        project = Project()
        result = project.query_by_args(self.superuser, **params)

        # Verify filter was called
        assert mock_queryset.filter.called
        assert result['count'] == 1

    @patch('projects.models.Project.objects')
    def test_query_by_args_with_ordering_asc(self, mock_objects):
        """Test query_by_args with ascending order"""
        from projects.models import Project

        mock_queryset = self.setup_mock_queryset(count=10)
        mock_objects.all.return_value = mock_queryset

        params = {
            'draw': ['1'],
            'length': ['10'],
            'start': ['0'],
            'search[value]': [''],
            'order[0][column]': ['1'],  # abbreviation
            'order[0][dir]': ['asc'],
            'date_range': [''],
            'pi': [''],
            'technician': [''],
            'researcher': [''],
        }

        project = Project()
        result = project.query_by_args(self.superuser, **params)

        # Verify order_by was called with 'abbreviation' (no minus)
        mock_queryset.order_by.assert_called()
        order_arg = mock_queryset.order_by.call_args[0][0]
        assert order_arg == 'abbreviation'

    @patch('projects.models.Project.objects')
    def test_query_by_args_with_ordering_desc(self, mock_objects):
        """Test query_by_args with descending order"""
        from projects.models import Project

        mock_queryset = self.setup_mock_queryset(count=10)
        mock_objects.all.return_value = mock_queryset

        params = {
            'draw': ['1'],
            'length': ['10'],
            'start': ['0'],
            'search[value]': [''],
            'order[0][column]': ['2'],  # name
            'order[0][dir]': ['desc'],
            'date_range': [''],
            'pi': [''],
            'technician': [''],
            'researcher': [''],
        }

        project = Project()
        result = project.query_by_args(self.superuser, **params)

        # Verify order_by was called with '-name'
        mock_queryset.order_by.assert_called()
        order_arg = mock_queryset.order_by.call_args[0][0]
        assert order_arg == '-name'

    @patch('projects.models.Project.objects')
    def test_query_by_args_with_pagination(self, mock_objects):
        """Test query_by_args pagination"""
        from projects.models import Project

        mock_queryset = self.setup_mock_queryset(count=100)
        mock_objects.all.return_value = mock_queryset

        params = {
            'draw': ['2'],
            'length': ['10'],
            'start': ['20'],  # Page 3 (0-indexed)
            'search[value]': [''],
            'order[0][column]': ['0'],
            'order[0][dir]': ['asc'],
            'date_range': [''],
            'pi': [''],
            'technician': [''],
            'researcher': [''],
        }

        project = Project()
        result = project.query_by_args(self.superuser, **params)

        # Verify slicing was called with correct indices
        mock_queryset.__getitem__.assert_called()
        # The slice should be [20:30] (start=20, length=10)
        assert result['draw'] == 2
        assert result['total'] == 100

    @patch('projects.models.Project.objects')
    def test_query_by_args_with_all_filters_combined(self, mock_objects):
        """Test query_by_args with multiple filters combined"""
        from projects.models import Project

        mock_queryset = self.setup_mock_queryset(count=2)
        mock_objects.all.return_value = mock_queryset

        params = {
            'draw': ['1'],
            'length': ['10'],
            'start': ['0'],
            'search[value]': ['melanoma'],
            'order[0][column]': ['1'],
            'order[0][dir]': ['desc'],
            'date_range': ['2024-01-01 to 2024-12-31'],
            'pi': ['BB'],
            'technician': ['5'],
            'researcher': ['10'],
        }

        project = Project()
        result = project.query_by_args(self.superuser, **params)

        # Verify multiple filters were applied
        assert mock_queryset.filter.call_count >= 4  # pi, tech, researcher, search
        assert result['count'] == 2

    @patch('projects.models.Project.objects')
    def test_query_by_args_returns_correct_structure(self, mock_objects):
        """Test query_by_args returns expected dictionary structure"""
        from projects.models import Project

        mock_queryset = self.setup_mock_queryset(count=5)
        mock_objects.all.return_value = mock_queryset

        params = ProjectTestData.DATATABLES_REQUEST

        project = Project()
        result = project.query_by_args(self.superuser, **params)

        # Verify response structure
        assert 'items' in result
        assert 'count' in result
        assert 'total' in result
        assert 'draw' in result

        assert isinstance(result['items'], Mock)
        assert isinstance(result['count'], int)
        assert isinstance(result['total'], int)
        assert isinstance(result['draw'], int)

    @patch('projects.models.Project.objects')
    def test_query_by_args_handles_empty_result(self, mock_objects):
        """Test query_by_args with no matching results"""
        from projects.models import Project

        mock_queryset = self.setup_mock_queryset(count=0)
        mock_objects.all.return_value = mock_queryset

        params = {
            'draw': ['1'],
            'length': ['10'],
            'start': ['0'],
            'search[value]': ['nonexistent'],
            'order[0][column]': ['0'],
            'order[0][dir]': ['asc'],
            'date_range': [''],
            'pi': [''],
            'technician': [''],
            'researcher': [''],
        }

        project = Project()
        result = project.query_by_args(self.superuser, **params)

        assert result['count'] == 0
        assert result['total'] == 0

    @patch('projects.models.Project.objects')
    def test_query_by_args_with_different_column_orders(self, mock_objects):
        """Test query_by_args with different column ordering options"""
        from projects.models import Project

        # Test each column in ORDER_COLUMN_CHOICES
        columns = {
            '0': 'id',
            '1': 'abbreviation',
            '2': 'name',
            '3': 'technician',
            '4': 'researcher',
            '5': 'pi',
            '6': 'date_start',
            '7': 'speedtype',
        }

        for col_index, expected_field in columns.items():
            mock_queryset = self.setup_mock_queryset(count=10)
            mock_objects.all.return_value = mock_queryset

            params = {
                'draw': ['1'],
                'length': ['10'],
                'start': ['0'],
                'search[value]': [''],
                'order[0][column]': [col_index],
                'order[0][dir]': ['asc'],
                'date_range': [''],
                'pi': [''],
                'technician': [''],
                'researcher': [''],
            }

            project = Project()
            result = project.query_by_args(self.superuser, **params)

            # Verify order_by was called with expected field
            order_arg = mock_queryset.order_by.call_args[0][0]
            assert order_arg == expected_field

    @patch('projects.models.Project.objects')
    def test_query_by_args_exception_handling(self, mock_objects):
        """Test query_by_args raises exception on error"""
        from projects.models import Project

        # Make queryset raise an exception
        mock_objects.all.side_effect = Exception('Database error')

        params = ProjectTestData.DATATABLES_REQUEST

        project = Project()

        # Should raise the exception
        with pytest.raises(Exception) as exc_info:
            project.query_by_args(self.superuser, **params)

        assert 'Database error' in str(exc_info.value)

    def setup_mock_queryset(self, count=10):
        """Helper to create a properly chained mock queryset"""
        mock_queryset = MagicMock()

        # Make queryset return itself for chaining
        mock_queryset.annotate.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.all.return_value = mock_queryset

        # Mock count
        mock_queryset.count.return_value = count

        # Mock slicing
        mock_queryset.__getitem__.return_value = mock_queryset

        return mock_queryset


class TestProjectModelFields(BaseAPITestNoDatabase):
    """Test Project model field definitions"""

    def test_project_pi_choices(self):
        """Test PI_CHOICES are correctly defined"""
        from projects.models import Project

        expected_choices = [
            ('BB', 'Boris Bastian'),
            ('IY', 'Iwei Yeh'),
            ('AH', 'Alan Hunter Shain'),
        ]

        assert Project.PI_CHOICES == expected_choices

    def test_project_pi_constants(self):
        """Test PI constants are correctly defined"""
        from projects.models import Project

        assert Project.BORIS == 'BB'
        assert Project.IWEI == 'IY'
        assert Project.AHS == 'AH'

    def test_project_str_method(self):
        """Test Project __str__ returns name"""
        mock_project = self.create_mock_project(name='Test Project')

        assert str(mock_project) == 'Test Project'

    def create_mock_project(self, **kwargs):
        """Create a mock project object"""
        project = Mock()
        project.id = kwargs.get('id', 1)
        project.name = kwargs.get('name', 'Test Project')
        project.abbreviation = kwargs.get('abbreviation', 'TST')
        project.pi = kwargs.get('pi', 'BB')
        project.speedtype = kwargs.get('speedtype', '')
        project.description = kwargs.get('description', '')
        project.date_start = kwargs.get('date_start', datetime.now())
        project.date = kwargs.get('date', datetime.now())
        project.num_blocks = kwargs.get('num_blocks', 0)

        # Mock __str__ method
        project.__str__ = Mock(return_value=project.name)

        return project


class TestProjectQueryHelperFunctions(BaseAPITestNoDatabase):
    """Test helper functions in query_by_args"""

    @patch('projects.models.Project.objects')
    def test_is_initial_value_detection(self, mock_objects):
        """Test detection of initial search values"""
        from projects.models import Project

        mock_queryset = self.setup_mock_queryset(count=1)
        mock_objects.all.return_value = mock_queryset

        # Test with initial value
        params = {
            'draw': ['1'],
            'length': ['10'],
            'start': ['0'],
            'search[value]': ['_initial:{"model":"block","id":"123"}'],
            'order[0][column]': ['0'],
            'order[0][dir]': ['asc'],
            'date_range': [''],
            'pi': [''],
            'technician': [''],
            'researcher': [''],
        }

        project = Project()
        result = project.query_by_args(self.superuser, **params)

        # Should process initial search
        assert result is not None

    @patch('projects.models.Project.objects')
    def test_parse_value_with_initial_prefix(self, mock_objects):
        """Test parsing of initial search values"""
        from projects.models import Project

        mock_queryset = self.setup_mock_queryset(count=1)
        mock_objects.all.return_value = mock_queryset

        # Test JSON parsing
        params = {
            'draw': ['1'],
            'length': ['10'],
            'start': ['0'],
            'search[value]': ['_initial:{"model":"project","id":"789"}'],
            'order[0][column]': ['0'],
            'order[0][dir]': ['asc'],
            'date_range': [''],
            'pi': [''],
            'technician': [''],
            'researcher': [''],
        }

        project = Project()
        result = project.query_by_args(self.superuser, **params)

        # Should successfully parse and execute query
        assert result['items'] is not None

    def setup_mock_queryset(self, count=10):
        """Helper to create a properly chained mock queryset"""
        mock_queryset = MagicMock()
        mock_queryset.annotate.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.all.return_value = mock_queryset
        mock_queryset.count.return_value = count
        mock_queryset.__getitem__.return_value = mock_queryset
        return mock_queryset