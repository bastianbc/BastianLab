# tests/utils/base_test.py
"""
Base Test Classes - No Database Required
"""
import unittest
from unittest.mock import Mock
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.backends.base import SessionBase
from django.http import QueryDict

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test1.settings")
django.setup()


# tests/conftest.py (update the MockRequest class)

class MockRequest:
    """Mock Django request object that mimics django.http.HttpRequest"""

    def __init__(self, method='GET', path='/', data=None, user=None, get_params=None, post_params=None):
        self.method = method.upper()
        self.path = path
        self.path_info = path
        self.user = user or AnonymousUser()

        # Handle GET parameters
        if get_params:
            self.GET = QueryDict(mutable=True)
            for key, value in get_params.items():
                if isinstance(value, list):
                    self.GET.setlist(key, value)
                else:
                    self.GET[key] = value
        else:
            self.GET = QueryDict()

        # Handle POST parameters
        if post_params:
            self.POST = QueryDict(mutable=True)
            for key, value in post_params.items():
                if isinstance(value, list):
                    self.POST.setlist(key, value)
                else:
                    self.POST[key] = value
        elif data:
            self.POST = QueryDict(mutable=True)
            for key, value in data.items():
                if isinstance(value, list):
                    self.POST.setlist(key, value)
                else:
                    self.POST[key] = value
        else:
            self.POST = QueryDict()

        # Session
        self.session = SessionBase()

        # Messages
        self._messages = FallbackStorage(self)

        # Meta
        self.META = {
            'REMOTE_ADDR': '127.0.0.1',
            'HTTP_USER_AGENT': 'Test Client',
            'SERVER_NAME': 'testserver',
            'SERVER_PORT': '80',
        }

        # Request attributes
        self.resolver_match = None
        self.content_type = 'text/html'
        self.content_params = {}

    def build_absolute_uri(self, location=None):
        """Mock build_absolute_uri"""
        if location:
            return f'http://testserver{location}'
        return f'http://testserver{self.path}'

    def get_full_path(self):
        """Return the full path including query string"""
        query_string = self.GET.urlencode()
        if query_string:
            return f'{self.path}?{query_string}'
        return self.path

    def get_full_path_info(self):
        """Return path_info with query string"""
        return self.get_full_path()

    def is_secure(self):
        """Return whether request is secure (HTTPS)"""
        return False

    def is_ajax(self):
        """Return whether request is AJAX"""
        return self.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

    def get_host(self):
        """Return the HTTP host"""
        return 'testserver'

    def get_port(self):
        """Return the server port"""
        return '80'

    def scheme(self):
        """Return the scheme (http or https)"""
        return 'http'


class BaseViewTestNoDatabase(unittest.TestCase):
    """
    Base test class for view testing WITHOUT database
    Uses unittest.TestCase instead of Django's TestCase
    """

    def setUp(self):
        """Set up test fixtures without database"""
        # Create mock users
        self.user = self.create_mock_user(
            id=1,
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            is_superuser=False,
            is_staff=False
        )

        self.user_with_perms = self.create_mock_user(
            id=2,
            username='permuser',
            email='perm@example.com',
            first_name='Perm',
            last_name='User',
            is_superuser=False,
            is_staff=True
        )

        self.superuser = self.create_mock_user(
            id=3,
            username='admin',
            email='admin@example.com',
            first_name='Admin',
            last_name='Super',
            is_superuser=True,
            is_staff=True
        )

        self.user_no_perms = self.create_mock_user(
            id=4,
            username='nopermuser',
            email='noperm@example.com',
            first_name='NoPerm',
            last_name='User',
            is_superuser=False,
            is_staff=False
        )

        self.anonymous_user = AnonymousUser()

    def create_mock_user(self, id=1, username='testuser', email='test@example.com',
                         first_name='Test', last_name='User', is_superuser=False, is_staff=False):
        """Create a mock user object"""
        user = Mock()
        user.id = id
        user.pk = id
        user.username = username
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.is_superuser = is_superuser
        user.is_staff = is_staff
        user.is_active = True
        user.is_authenticated = True
        user.get_full_name = Mock(return_value=f"{first_name} {last_name}")
        user.has_perm = Mock(return_value=is_superuser)  # Superuser has all perms
        user.has_perms = Mock(return_value=is_superuser)
        user.groups = Mock()
        user.groups.all = Mock(return_value=[])
        user.user_permissions = Mock()
        user.user_permissions.all = Mock(return_value=[])
        return user

    def create_request(self, method='GET', path='/', data=None, user=None,
                       get_params=None, post_params=None):
        """
        Create a mock request object

        Args:
            method (str): HTTP method (GET, POST, etc.)
            path (str): Request path
            data (dict): POST data (deprecated, use post_params)
            user: User object
            get_params (dict): GET parameters
            post_params (dict): POST parameters

        Returns:
            MockRequest object
        """
        if user is None:
            user = self.user

        return MockRequest(
            method=method,
            path=path,
            data=data,
            user=user,
            get_params=get_params,
            post_params=post_params
        )

    def grant_permission(self, user, permission_name):
        """Mock granting permission to user"""
        user.has_perm = Mock(return_value=True)
        user.has_perms = Mock(return_value=True)


class BaseAPITestNoDatabase(BaseViewTestNoDatabase):
    """Base test class for API testing without database"""

    def assertJSONResponse(self, response, expected_status=200):
        """Assert response is JSON with expected status"""
        assert response.status_code == expected_status
        content_type = response.get('Content-Type', '')
        assert 'application/json' in content_type

    def assertJSONEqual(self, response, expected_data):
        """Assert JSON response equals expected data"""
        import json
        actual_data = json.loads(response.content)
        assert actual_data == expected_data

    def assertJSONContains(self, response, key):
        """Assert JSON response contains key"""
        import json
        data = json.loads(response.content)
        assert key in data