# tests/unit/account/test_urls.py
"""
Account URLs Test Cases - No Database Required
"""
import pytest
from django.urls import reverse, resolve
from tests.utils.base_test import BaseAPITestNoDatabase


class TestAccountUrls(BaseAPITestNoDatabase):
    """Test account URL patterns"""

    def test_accounts_url_resolves(self):
        """Test accounts URL resolves to correct view"""
        from account import views

        url = reverse('accounts')
        resolved = resolve(url)

        assert resolved.func == views.accounts

    def test_new_account_url_resolves(self):
        """Test new-account URL resolves to correct view"""
        from account import views

        url = reverse('new-account')
        resolved = resolve(url)

        assert resolved.func == views.new_account

    def test_edit_account_url_resolves(self):
        """Test edit-account URL resolves to correct view"""
        from account import views

        url = reverse('edit-account', args=[1])
        resolved = resolve(url)

        assert resolved.func == views.edit_account

    def test_delete_account_url_resolves(self):
        """Test delete-account URL resolves to correct view"""
        from account import views

        url = reverse('delete-account', args=[1])
        resolved = resolve(url)

        assert resolved.func == views.delete_account

    def test_filter_accounts_url_resolves(self):
        """Test filter-accounts URL resolves to correct view"""
        from account import views

        url = reverse('filter-accounts')
        resolved = resolve(url)

        assert resolved.func == views.filter_accounts

    def test_reset_password_url_resolves(self):
        """Test reset-password URL resolves to correct view"""
        from account import views

        url = reverse('reset-password', args=[1])
        resolved = resolve(url)

        assert resolved.func == views.reset_password


class TestAccountUrlPatterns(BaseAPITestNoDatabase):
    """Test URL patterns structure"""

    def test_accounts_url_pattern(self):
        """Test accounts URL pattern"""
        url = reverse('accounts')
        assert url == '/account/'

    def test_new_account_url_pattern(self):
        """Test new-account URL pattern"""
        url = reverse('new-account')
        assert url == '/account/new'

    def test_edit_account_url_pattern(self):
        """Test edit-account URL pattern with ID"""
        url = reverse('edit-account', args=[42])
        assert url == '/account/edit/42'

    def test_delete_account_url_pattern(self):
        """Test delete-account URL pattern with ID"""
        url = reverse('delete-account', args=[99])
        assert url == '/account/delete/99'

    def test_filter_accounts_url_pattern(self):
        """Test filter-accounts URL pattern"""
        url = reverse('filter-accounts')
        assert url == '/account/filter_accounts'

    def test_reset_password_url_pattern(self):
        """Test reset-password URL pattern with ID"""
        url = reverse('reset-password', args=[123])
        assert url == '/account/reset_password/123'


class TestAccountUrlReverse(BaseAPITestNoDatabase):
    """Test URL reverse functionality"""

    def test_accounts_url_reverse(self):
        """Test accounts URL can be reversed by name"""
        url = reverse('accounts')
        assert url is not None

    def test_new_account_url_reverse(self):
        """Test new-account URL can be reversed by name"""
        url = reverse('new-account')
        assert url is not None

    def test_edit_account_url_reverse_with_args(self):
        """Test edit-account URL can be reversed with args"""
        url = reverse('edit-account', args=[1])
        assert url is not None
        assert '/edit/1' in url

    def test_delete_account_url_reverse_with_args(self):
        """Test delete-account URL can be reversed with args"""
        url = reverse('delete-account', args=[1])
        assert url is not None
        assert '/delete/1' in url

    def test_filter_accounts_url_reverse(self):
        """Test filter-accounts URL can be reversed by name"""
        url = reverse('filter-accounts')
        assert url is not None

    def test_reset_password_url_reverse_with_args(self):
        """Test reset-password URL can be reversed with args"""
        url = reverse('reset-password', args=[1])
        assert url is not None
        assert '/reset_password/1' in url


class TestAccountUrlNames(BaseAPITestNoDatabase):
    """Test URL names are correctly defined"""

    def test_accounts_url_name(self):
        """Test accounts URL name"""
        url = reverse('accounts')
        resolved = resolve(url)
        assert resolved.url_name == 'accounts'

    def test_new_account_url_name(self):
        """Test new-account URL name"""
        url = reverse('new-account')
        resolved = resolve(url)
        assert resolved.url_name == 'new-account'

    def test_edit_account_url_name(self):
        """Test edit-account URL name"""
        url = reverse('edit-account', args=[1])
        resolved = resolve(url)
        assert resolved.url_name == 'edit-account'

    def test_delete_account_url_name(self):
        """Test delete-account URL name"""
        url = reverse('delete-account', args=[1])
        resolved = resolve(url)
        assert resolved.url_name == 'delete-account'

    def test_filter_accounts_url_name(self):
        """Test filter-accounts URL name"""
        url = reverse('filter-accounts')
        resolved = resolve(url)
        assert resolved.url_name == 'filter-accounts'

    def test_reset_password_url_name(self):
        """Test reset-password URL name"""
        url = reverse('reset-password', args=[1])
        resolved = resolve(url)
        assert resolved.url_name == 'reset-password'


class TestAccountUrlParameters(BaseAPITestNoDatabase):
    """Test URL parameters are correctly parsed"""

    def test_edit_account_url_extracts_id(self):
        """Test edit-account URL extracts ID parameter"""
        url = '/account/edit/42'
        resolved = resolve(url)

        assert 'id' in resolved.kwargs
        assert resolved.kwargs['id'] == 42

    def test_delete_account_url_extracts_id(self):
        """Test delete-account URL extracts ID parameter"""
        url = '/account/delete/99'
        resolved = resolve(url)

        assert 'id' in resolved.kwargs
        assert resolved.kwargs['id'] == 99

    def test_reset_password_url_extracts_id(self):
        """Test reset-password URL extracts ID parameter"""
        url = '/account/reset_password/123'
        resolved = resolve(url)

        assert 'id' in resolved.kwargs
        assert resolved.kwargs['id'] == 123

    def test_edit_account_url_with_different_ids(self):
        """Test edit-account URL works with different IDs"""
        for test_id in [1, 100, 999]:
            url = reverse('edit-account', args=[test_id])
            resolved = resolve(url)
            assert resolved.kwargs['id'] == test_id

    def test_delete_account_url_with_different_ids(self):
        """Test delete-account URL works with different IDs"""
        for test_id in [5, 50, 500]:
            url = reverse('delete-account', args=[test_id])
            resolved = resolve(url)
            assert resolved.kwargs['id'] == test_id

    def test_reset_password_url_with_different_ids(self):
        """Test reset-password URL works with different IDs"""
        for test_id in [10, 20, 30]:
            url = reverse('reset-password', args=[test_id])
            resolved = resolve(url)
            assert resolved.kwargs['id'] == test_id
