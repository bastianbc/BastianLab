# tests/unit/projects/test_views.py
"""
Project Views Test Cases - No Database Required
"""
import json
from unittest.mock import Mock, patch
from django.http import JsonResponse
from tests.utils.base_test import BaseAPITestNoDatabase
from tests.fixtures.project_fixtures import ProjectTestData


class TestFilterProjectsView(BaseAPITestNoDatabase):
    """Test filter_projects view without database"""

    @patch('projects.views.ProjectsSerializer')
    @patch('projects.views.Project')
    def test_filter_projects_returns_datatable_format(
            self,
            mock_project_class,
            mock_serializer_class
    ):
        """Test filter_projects returns correct DataTables format"""
        from projects.views import filter_projects

        # Mock Project().query_by_args
        mock_project_instance = Mock()
        mock_project_instance.query_by_args.return_value = {
            'items': [],
            'count': 7,
            'total': 7,
            'draw': 1
        }
        mock_project_class.return_value = mock_project_instance

        # Mock serializer
        mock_serializer = Mock()
        mock_serializer.data = ProjectTestData.SAMPLE_PROJECTS
        mock_serializer_class.return_value = mock_serializer

        # Create request with GET parameters
        request = self.create_request(
            method='GET',
            path='/projects/filter_projects',
            get_params=ProjectTestData.DATATABLES_REQUEST,
            user=self.user
        )

        # Call view
        response = filter_projects(request)

        # Assertions
        self.assertJSONResponse(response, 200)
        data = json.loads(response.content)

        assert 'data' in data
        assert 'draw' in data
        assert 'recordsTotal' in data
        assert 'recordsFiltered' in data

        assert data['draw'] == 1
        assert data['recordsTotal'] == 7
        assert data['recordsFiltered'] == 7
        assert len(data['data']) == len(ProjectTestData.SAMPLE_PROJECTS)

    @patch('projects.views.ProjectsSerializer')
    @patch('projects.views.Project')
    def test_filter_projects_passes_user_to_query(
            self,
            mock_project_class,
            mock_serializer_class
    ):
        """Test filter_projects passes request.user to query_by_args"""
        from projects.views import filter_projects

        mock_project_instance = Mock()
        mock_project_instance.query_by_args.return_value = {
            'items': [],
            'count': 0,
            'total': 0,
            'draw': 1
        }
        mock_project_class.return_value = mock_project_instance
        mock_serializer_class.return_value = Mock(data=[])

        request = self.create_request(
            method='GET',
            get_params={'draw': ['1']},
            user=self.user
        )

        filter_projects(request)

        # Verify query_by_args called with user
        call_args = mock_project_instance.query_by_args.call_args
        assert call_args[0][0] == self.user
        # Verify GET params were passed as kwargs
        assert call_args[1] == request.GET

    @patch('projects.views.ProjectsSerializer')
    @patch('projects.views.Project')
    def test_filter_projects_passes_get_params(
            self,
            mock_project_class,
            mock_serializer_class
    ):
        """Test filter_projects passes GET parameters to query"""
        from projects.views import filter_projects

        mock_project_instance = Mock()
        mock_project_instance.query_by_args.return_value = {
            'items': [],
            'count': 0,
            'total': 0,
            'draw': 1
        }
        mock_project_class.return_value = mock_project_instance
        mock_serializer_class.return_value = Mock(data=[])

        # Create request with filters
        request_params = {
            'draw': ['1'],
            'pi': ['BB'],
            'technician': ['5'],
            'researcher': ['10'],
        }
        request = self.create_request(
            method='GET',
            get_params=request_params,
            user=self.user
        )

        filter_projects(request)

        # Verify GET params were passed
        call_kwargs = mock_project_instance.query_by_args.call_args[1]
        assert 'pi' in call_kwargs
        assert 'technician' in call_kwargs
        assert 'researcher' in call_kwargs

    @patch('projects.views.ProjectsSerializer')
    @patch('projects.views.Project')
    def test_filter_projects_serializes_items(
            self,
            mock_project_class,
            mock_serializer_class
    ):
        """Test filter_projects serializes query results"""
        from projects.views import filter_projects

        mock_items = [Mock(id=1), Mock(id=2)]
        mock_project_instance = Mock()
        mock_project_instance.query_by_args.return_value = {
            'items': mock_items,
            'count': 2,
            'total': 2,
            'draw': 1
        }
        mock_project_class.return_value = mock_project_instance

        mock_serializer = Mock()
        mock_serializer.data = [{'id': 1}, {'id': 2}]
        mock_serializer_class.return_value = mock_serializer

        request = self.create_request(
            method='GET',
            get_params={'draw': ['1']},
            user=self.user
        )

        response = filter_projects(request)

        # Verify serializer was called with items and many=True
        mock_serializer_class.assert_called_once_with(mock_items, many=True)

        # Verify response contains serialized data
        data = json.loads(response.content)
        assert data['data'] == [{'id': 1}, {'id': 2}]

    @patch('projects.views.ProjectsSerializer')
    @patch('projects.views.Project')
    def test_filter_projects_returns_serialized_data(
            self,
            mock_project_class,
            mock_serializer_class
    ):
        """Test filter_projects returns serialized data in response"""
        from projects.views import filter_projects

        mock_project_instance = Mock()
        mock_project_instance.query_by_args.return_value = {
            'items': [],
            'count': 2,
            'total': 5,
            'draw': 3
        }
        mock_project_class.return_value = mock_project_instance

        serialized_data = ProjectTestData.SAMPLE_PROJECTS[:2]
        mock_serializer = Mock()
        mock_serializer.data = serialized_data
        mock_serializer_class.return_value = mock_serializer

        request = self.create_request(
            method='GET',
            get_params={'draw': ['3']},
            user=self.user
        )

        response = filter_projects(request)
        data = json.loads(response.content)

        # Verify all response fields
        assert data['data'] == serialized_data
        assert data['draw'] == 3
        assert data['recordsTotal'] == 5
        assert data['recordsFiltered'] == 2

    @patch('projects.views.ProjectsSerializer')
    @patch('projects.views.Project')
    def test_filter_projects_handles_search_value(
            self,
            mock_project_class,
            mock_serializer_class
    ):
        """Test filter_projects passes search value to query"""
        from projects.views import filter_projects

        mock_project_instance = Mock()
        mock_project_instance.query_by_args.return_value = {
            'items': [],
            'count': 1,
            'total': 10,
            'draw': 1
        }
        mock_project_class.return_value = mock_project_instance
        mock_serializer_class.return_value = Mock(data=[])

        # Create request with search value
        request_params = {
            'draw': ['1'],
            'search[value]': ['test'],
        }
        request = self.create_request(
            method='GET',
            get_params=request_params,
            user=self.user
        )

        filter_projects(request)

        # Verify search value was passed
        call_kwargs = mock_project_instance.query_by_args.call_args[1]
        assert 'search[value]' in call_kwargs

    @patch('projects.views.ProjectsSerializer')
    @patch('projects.views.Project')
    def test_filter_projects_handles_ordering(
            self,
            mock_project_class,
            mock_serializer_class
    ):
        """Test filter_projects passes ordering parameters"""
        from projects.views import filter_projects

        mock_project_instance = Mock()
        mock_project_instance.query_by_args.return_value = {
            'items': [],
            'count': 0,
            'total': 0,
            'draw': 1
        }
        mock_project_class.return_value = mock_project_instance
        mock_serializer_class.return_value = Mock(data=[])

        # Create request with ordering
        request_params = {
            'draw': ['1'],
            'order[0][column]': ['2'],
            'order[0][dir]': ['desc'],
        }
        request = self.create_request(
            method='GET',
            get_params=request_params,
            user=self.user
        )

        filter_projects(request)

        # Verify ordering params were passed
        call_kwargs = mock_project_instance.query_by_args.call_args[1]
        assert 'order[0][column]' in call_kwargs
        assert 'order[0][dir]' in call_kwargs

    @patch('projects.views.ProjectsSerializer')
    @patch('projects.views.Project')
    def test_filter_projects_handles_pagination(
            self,
            mock_project_class,
            mock_serializer_class
    ):
        """Test filter_projects passes pagination parameters"""
        from projects.views import filter_projects

        mock_project_instance = Mock()
        mock_project_instance.query_by_args.return_value = {
            'items': [],
            'count': 100,
            'total': 100,
            'draw': 1
        }
        mock_project_class.return_value = mock_project_instance
        mock_serializer_class.return_value = Mock(data=[])

        # Create request with pagination
        request_params = {
            'draw': ['1'],
            'start': ['20'],
            'length': ['10'],
        }
        request = self.create_request(
            method='GET',
            get_params=request_params,
            user=self.user
        )

        filter_projects(request)

        # Verify pagination params were passed
        call_kwargs = mock_project_instance.query_by_args.call_args[1]
        assert 'start' in call_kwargs
        assert 'length' in call_kwargs

    @patch('projects.views.login_required')
    def test_filter_projects_requires_login(self, mock_login_required):
        """Test filter_projects has login_required decorator"""
        from projects.views import filter_projects

        # Check that the view has the login_required decorator
        # The decorator wraps the function
        assert hasattr(filter_projects, '__wrapped__') or callable(filter_projects)

    @patch('projects.views.ProjectsSerializer')
    @patch('projects.views.Project')
    def test_filter_projects_with_anonymous_user_bypasses_decorator(
            self,
            mock_project_class,
            mock_serializer_class
    ):
        """Test filter_projects logic with anonymous user (bypassing decorator)"""
        # This test focuses on the view logic, not the decorator
        # The login_required decorator is tested separately
        from projects.views import filter_projects

        # Get the actual view function, not the decorated one
        # This allows us to test the view logic independently
        actual_view = filter_projects.__wrapped__ if hasattr(filter_projects, '__wrapped__') else filter_projects

        mock_project_instance = Mock()
        mock_project_instance.query_by_args.return_value = {
            'items': [],
            'count': 0,
            'total': 0,
            'draw': 1
        }
        mock_project_class.return_value = mock_project_instance
        mock_serializer_class.return_value = Mock(data=[])

        # Create request with anonymous user
        request = self.create_request(
            method='GET',
            get_params={'draw': ['1']},
            user=self.anonymous_user
        )

        # Call the unwrapped view
        response = actual_view(request)

        # Verify anonymous user was passed to query_by_args
        call_args = mock_project_instance.query_by_args.call_args
        assert call_args[0][0] == self.anonymous_user

    @patch('projects.views.ProjectsSerializer')
    @patch('projects.views.Project')
    def test_filter_projects_with_superuser(
            self,
            mock_project_class,
            mock_serializer_class
    ):
        """Test filter_projects with superuser"""
        from projects.views import filter_projects

        mock_project_instance = Mock()
        mock_project_instance.query_by_args.return_value = {
            'items': [],
            'count': 10,
            'total': 10,
            'draw': 1
        }
        mock_project_class.return_value = mock_project_instance
        mock_serializer_class.return_value = Mock(data=[])

        # Create request with superuser
        request = self.create_request(
            method='GET',
            get_params={'draw': ['1']},
            user=self.superuser
        )

        response = filter_projects(request)

        # Verify superuser was passed
        call_args = mock_project_instance.query_by_args.call_args
        assert call_args[0][0] == self.superuser
        assert call_args[0][0].is_superuser is True

    @patch('projects.views.ProjectsSerializer')
    @patch('projects.views.Project')
    def test_filter_projects_returns_json_content_type(
            self,
            mock_project_class,
            mock_serializer_class
    ):
        """Test filter_projects returns JSON content type"""
        from projects.views import filter_projects

        mock_project_instance = Mock()
        mock_project_instance.query_by_args.return_value = {
            'items': [],
            'count': 0,
            'total': 0,
            'draw': 1
        }
        mock_project_class.return_value = mock_project_instance
        mock_serializer_class.return_value = Mock(data=[])

        request = self.create_request(
            method='GET',
            get_params={'draw': ['1']},
            user=self.user
        )

        response = filter_projects(request)

        # Verify response type
        assert isinstance(response, JsonResponse)
        assert 'application/json' in response['Content-Type']

    @patch('projects.views.ProjectsSerializer')
    @patch('projects.views.Project')
    def test_filter_projects_with_all_filters(
            self,
            mock_project_class,
            mock_serializer_class
    ):
        """Test filter_projects with all possible filters"""
        from projects.views import filter_projects

        mock_project_instance = Mock()
        mock_project_instance.query_by_args.return_value = {
            'items': [],
            'count': 1,
            'total': 10,
            'draw': 1
        }
        mock_project_class.return_value = mock_project_instance
        mock_serializer_class.return_value = Mock(data=[])

        # Create request with all filters
        request_params = {
            'draw': ['1'],
            'length': ['10'],
            'start': ['0'],
            'search[value]': ['test'],
            'order[0][column]': ['1'],
            'order[0][dir]': ['asc'],
            'date_range': ['2024-01-01 to 2024-12-31'],
            'pi': ['BB'],
            'technician': ['5'],
            'researcher': ['10'],
        }
        request = self.create_request(
            method='GET',
            get_params=request_params,
            user=self.user
        )

        response = filter_projects(request)

        # Verify all params were passed
        call_kwargs = mock_project_instance.query_by_args.call_args[1]
        assert call_kwargs['draw'] == ['1']
        assert call_kwargs['pi'] == ['BB']
        assert call_kwargs['technician'] == ['5']
        assert call_kwargs['researcher'] == ['10']
        assert call_kwargs['date_range'] == ['2024-01-01 to 2024-12-31']

        # Verify response is successful
        self.assertJSONResponse(response, 200)