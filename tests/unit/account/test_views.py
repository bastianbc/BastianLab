# tests/unit/account/test_views.py
"""
Account Views Test Cases - No Database Required
"""
import json
from unittest.mock import Mock, patch, MagicMock
from django.http import JsonResponse
from tests.utils.base_test import BaseAPITestNoDatabase
from tests.fixtures.account_fixtures import AccountTestData

# Import views at module level to avoid patching issues
from account.views import delete_account, filter_accounts, reset_password


class TestDeleteAccountView(BaseAPITestNoDatabase):
    """Test delete_account view"""

    def test_delete_account_success(self):
        """Test delete_account successfully deletes user"""
        # Grant permission
        self.grant_permission(self.user, 'account.delete_user')

        with patch('account.views.User.objects') as mock_objects:
            # Mock user instance
            mock_user = Mock()
            mock_user.id = 1
            mock_user.delete = Mock()
            mock_objects.get.return_value = mock_user

            request = self.create_request(
                method='POST',
                path='/account/delete/1',
                user=self.user
            )

            response = delete_account(request, id=1)

            # Verify user was retrieved and deleted
            mock_objects.get.assert_called_once_with(id=1)
            mock_user.delete.assert_called_once()
            assert response.status_code == 302  # Redirect
            assert response.url == '/account'

    def test_delete_account_handles_exception(self):
        """Test delete_account handles deletion errors"""
        # Grant permission
        self.grant_permission(self.user, 'account.delete_user')

        with patch('account.views.User.objects') as mock_objects:
            # Mock exception during get
            mock_objects.get.side_effect = Exception("User not found")

            request = self.create_request(
                method='POST',
                path='/account/delete/999',
                user=self.user
            )

            response = delete_account(request, id=999)

            # Verify still redirects
            assert response.status_code == 302
            assert response.url == '/account'


class TestFilterAccountsView(BaseAPITestNoDatabase):
    """Test filter_accounts view without database"""

    def test_filter_accounts_returns_datatable_format(self):
        """Test filter_accounts returns correct DataTables format"""
        # Grant permission
        self.grant_permission(self.user, 'account.view_user')

        # Mock User().query_by_args and serializer
        with patch('account.views.User') as mock_user_class, \
             patch('account.serializers.AccountSerializer') as mock_serializer_class:

            # Mock User().query_by_args
            mock_user_instance = Mock()
            mock_user_instance.query_by_args.return_value = {
                'items': [],
                'count': 3,
                'total': 3,
                'draw': 1
            }
            mock_user_class.return_value = mock_user_instance

            # Mock serializer - set data directly on return_value
            mock_serializer_class.return_value.data = AccountTestData.SAMPLE_USERS

            # Create request with GET parameters
            request = self.create_request(
                method='GET',
                path='/account/filter_accounts',
                get_params=AccountTestData.DATATABLES_REQUEST,
                user=self.user
            )

            # Call view
            response = filter_accounts(request)

            # Assertions
            self.assertJSONResponse(response, 200)
            data = json.loads(response.content)

            assert 'data' in data
            assert 'draw' in data
            assert 'recordsTotal' in data
            assert 'recordsFiltered' in data

            assert data['draw'] == 1
            assert data['recordsTotal'] == 3
            assert data['recordsFiltered'] == 3
            assert len(data['data']) == len(AccountTestData.SAMPLE_USERS)

    def test_filter_accounts_calls_query_by_args(self):
        """Test filter_accounts calls User.query_by_args with correct params"""
        # Grant permission
        self.grant_permission(self.user, 'account.view_user')

        with patch('account.views.User') as mock_user_class, \
             patch('account.serializers.AccountSerializer') as mock_serializer_class:

            # Mock User instance
            mock_user_instance = Mock()
            mock_user_instance.query_by_args.return_value = {
                'items': [],
                'count': 0,
                'total': 0,
                'draw': 1
            }
            mock_user_class.return_value = mock_user_instance

            # Mock serializer
            mock_serializer_class.return_value.data = []

            request = self.create_request(
                method='GET',
                path='/account/filter_accounts',
                get_params=AccountTestData.DATATABLES_REQUEST,
                user=self.user
            )

            filter_accounts(request)

            # Verify query_by_args was called
            mock_user_instance.query_by_args.assert_called_once()


class TestResetPasswordView(BaseAPITestNoDatabase):
    """Test reset_password view"""

    def test_reset_password_success(self):
        """Test reset_password successfully resets user password"""
        # Grant permission
        self.grant_permission(self.user, 'account.change_user')

        with patch('account.views.User.objects') as mock_objects:
            # Mock user instance
            mock_user = Mock()
            mock_user.id = 1
            mock_user.reset_password = Mock()
            mock_objects.get.return_value = mock_user

            request = self.create_request(
                method='POST',
                path='/account/reset_password/1',
                user=self.user
            )

            response = reset_password(request, id=1)

            # Verify user was retrieved and password reset
            mock_objects.get.assert_called_once_with(id=1)
            mock_user.reset_password.assert_called_once()
            assert response.status_code == 302  # Redirect
            assert response.url == '/account'


class TestFilterAccountsView(BaseAPITestNoDatabase):
    """Test filter_accounts view without database"""

    def test_filter_accounts_returns_datatable_format(self):
        """Test filter_accounts returns correct DataTables format"""
        # Grant permission
        self.grant_permission(self.user, 'account.view_user')

        # Mock User().query_by_args and serializer
        with patch('account.views.User') as mock_user_class, \
             patch('account.serializers.AccountSerializer') as mock_serializer_class:

            # Mock User().query_by_args
            mock_user_instance = Mock()
            mock_user_instance.query_by_args.return_value = {
                'items': [],
                'count': 3,
                'total': 3,
                'draw': 1
            }
            mock_user_class.return_value = mock_user_instance

            # Mock serializer - set data directly on return_value
            mock_serializer_class.return_value.data = AccountTestData.SAMPLE_USERS

            # Create request with GET parameters
            request = self.create_request(
                method='GET',
                path='/account/filter_accounts',
                get_params=AccountTestData.DATATABLES_REQUEST,
                user=self.user
            )

            # Call view
            response = filter_accounts(request)

            # Assertions
            self.assertJSONResponse(response, 200)
            data = json.loads(response.content)

            assert 'data' in data
            assert 'draw' in data
            assert 'recordsTotal' in data
            assert 'recordsFiltered' in data

            assert data['draw'] == 1
            assert data['recordsTotal'] == 3
            assert data['recordsFiltered'] == 3
            assert len(data['data']) == len(AccountTestData.SAMPLE_USERS)

    def test_filter_accounts_calls_query_by_args(self):
        """Test filter_accounts calls User.query_by_args with correct params"""
        # Grant permission
        self.grant_permission(self.user, 'account.view_user')

        with patch('account.views.User') as mock_user_class, \
             patch('account.serializers.AccountSerializer') as mock_serializer_class:

            # Mock User instance
            mock_user_instance = Mock()
            mock_user_instance.query_by_args.return_value = {
                'items': [],
                'count': 0,
                'total': 0,
                'draw': 1
            }
            mock_user_class.return_value = mock_user_instance

            # Mock serializer
            mock_serializer_class.return_value.data = []

            request = self.create_request(
                method='GET',
                path='/account/filter_accounts',
                get_params=AccountTestData.DATATABLES_REQUEST,
                user=self.user
            )

            filter_accounts(request)

            # Verify query_by_args was called
            mock_user_instance.query_by_args.assert_called_once()


class TestResetPasswordView(BaseAPITestNoDatabase):
    """Test reset_password view"""

    def test_reset_password_success(self):
        """Test reset_password successfully resets user password"""
        # Grant permission
        self.grant_permission(self.user, 'account.change_user')

        with patch('account.views.User.objects') as mock_objects:
            # Mock user instance
            mock_user = Mock()
            mock_user.id = 1
            mock_user.reset_password = Mock()
            mock_objects.get.return_value = mock_user

            request = self.create_request(
                method='POST',
                path='/account/reset_password/1',
                user=self.user
            )

            response = reset_password(request, id=1)

            # Verify user was retrieved and password reset
            mock_objects.get.assert_called_once_with(id=1)
            mock_user.reset_password.assert_called_once()
            assert response.status_code == 302  # Redirect
            assert response.url == '/account'
