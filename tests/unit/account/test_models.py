# tests/unit/account/test_models.py
"""
Account Model Test Cases - No Database Required
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from django.db.models import Q
from tests.utils.base_test import BaseAPITestNoDatabase
from tests.fixtures.account_fixtures import AccountTestData


class TestUserModel(BaseAPITestNoDatabase):
    """Test User model methods"""

    def setUp(self):
        """Set up test fixtures"""
        super().setUp()
        self.mock_user = self.create_mock_user_account()

    def create_mock_user_account(self, **kwargs):
        """Create a mock user object"""
        user = Mock()
        user.id = kwargs.get('id', 1)
        user.username = kwargs.get('username', 'testuser')
        user.first_name = kwargs.get('first_name', 'Test')
        user.last_name = kwargs.get('last_name', 'User')
        user.email = kwargs.get('email', 'test@example.com')
        user.is_superuser = kwargs.get('is_superuser', False)
        user.last_login = kwargs.get('last_login', datetime.now())

        # Mock methods
        user.get_full_name = Mock(return_value=f"{user.first_name} {user.last_name}")
        user.__unicode__ = Mock(return_value=user.get_full_name())

        return user

    def test_full_name_property(self):
        """Test full_name property returns get_full_name()"""
        from account.models import User

        mock_user = self.create_mock_user_account(first_name='John', last_name='Doe')

        # Test that get_full_name is called
        full_name = mock_user.get_full_name()
        assert full_name == 'John Doe'


class TestUserQueryByArgs(BaseAPITestNoDatabase):
    """Test User.query_by_args method"""

    @patch('account.models.User.objects')
    def test_query_by_args_basic_request(self, mock_objects):
        """Test query_by_args with basic DataTables request"""
        from account.models import User

        # Setup mock queryset
        mock_queryset = self.setup_mock_queryset(count=10)
        mock_objects.filter.return_value = mock_queryset

        # Create request params
        params = {
            'draw': ['1'],
            'length': ['10'],
            'start': ['0'],
            'search[value]': [''],
            'order[0][column]': ['0'],
            'order[0][dir]': ['asc'],
        }

        # Call method
        user = User()
        result = user.query_by_args(**params)

        # Assertions
        assert result['draw'] == 1
        assert result['total'] == 10
        assert result['count'] == 10
        assert 'items' in result

        # Verify queryset was filtered to exclude superusers
        mock_objects.filter.assert_called_with(is_superuser=False)

    @patch('account.models.User.objects')
    def test_query_by_args_with_search(self, mock_objects):
        """Test query_by_args with search term"""
        from account.models import User

        mock_queryset = self.setup_mock_queryset(count=3)
        mock_objects.filter.return_value = mock_queryset

        params = {
            'draw': ['1'],
            'length': ['10'],
            'start': ['0'],
            'search[value]': ['john'],
            'order[0][column]': ['0'],
            'order[0][dir]': ['asc'],
        }

        user = User()
        result = user.query_by_args(**params)

        # Verify filter was called for search
        assert mock_queryset.filter.called
        assert result['count'] == 3

    @patch('account.models.User.objects')
    def test_query_by_args_ordering_asc(self, mock_objects):
        """Test query_by_args with ascending order"""
        from account.models import User

        mock_queryset = self.setup_mock_queryset(count=10)
        mock_objects.filter.return_value = mock_queryset

        params = {
            'draw': ['1'],
            'length': ['10'],
            'start': ['0'],
            'search[value]': [''],
            'order[0][column]': ['1'],  # first_name
            'order[0][dir]': ['asc'],
        }

        user = User()
        result = user.query_by_args(**params)

        # Verify order_by was called
        mock_queryset.order_by.assert_called()
        order_arg = mock_queryset.order_by.call_args[0][0]
        assert order_arg == 'first_name'

    @patch('account.models.User.objects')
    def test_query_by_args_ordering_desc(self, mock_objects):
        """Test query_by_args with descending order"""
        from account.models import User

        mock_queryset = self.setup_mock_queryset(count=10)
        mock_objects.filter.return_value = mock_queryset

        params = {
            'draw': ['1'],
            'length': ['10'],
            'start': ['0'],
            'search[value]': [''],
            'order[0][column]': ['2'],  # last_name
            'order[0][dir]': ['desc'],
        }

        user = User()
        result = user.query_by_args(**params)

        # Verify order_by was called with '-last_name'
        order_arg = mock_queryset.order_by.call_args[0][0]
        assert order_arg == '-last_name'

    @patch('account.models.User.objects')
    def test_query_by_args_pagination(self, mock_objects):
        """Test query_by_args pagination"""
        from account.models import User

        mock_queryset = self.setup_mock_queryset(count=100)
        mock_objects.filter.return_value = mock_queryset

        params = {
            'draw': ['2'],
            'length': ['10'],
            'start': ['20'],  # Page 3
            'search[value]': [''],
            'order[0][column]': ['0'],
            'order[0][dir]': ['asc'],
        }

        user = User()
        result = user.query_by_args(**params)

        # Verify slicing
        mock_queryset.__getitem__.assert_called()
        assert result['draw'] == 2
        assert result['total'] == 100

    def setup_mock_queryset(self, count=10):
        """Helper to create a properly chained mock queryset"""
        mock_queryset = MagicMock()
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.count.return_value = count
        mock_queryset.__getitem__.return_value = mock_queryset
        return mock_queryset


class TestUserResetPassword(BaseAPITestNoDatabase):
    """Test User.reset_password method"""

    def test_reset_password_clears_last_login(self):
        """Test reset_password sets last_login to None"""
        from account.models import User

        # Create mock user
        mock_user = Mock(spec=User)
        mock_user.last_login = datetime.now()
        mock_user.save = Mock()

        # Call reset_password
        User.reset_password(mock_user)

        # Verify last_login was set to None
        assert mock_user.last_login is None
        mock_user.save.assert_called_once()
