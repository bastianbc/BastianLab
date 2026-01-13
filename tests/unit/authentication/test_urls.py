# tests/unit/authentication/test_urls.py
"""
Authentication URLs Test Cases - No Database Required
"""
import pytest
from django.urls import reverse, resolve
from tests.utils.base_test import BaseAPITestNoDatabase


class TestAuthenticationUrls(BaseAPITestNoDatabase):
    """Test authentication URL patterns"""

    def test_login_url_resolves(self):
        """Test login URL resolves to correct view"""
        from authentication import views

        url = reverse('login')
        resolved = resolve(url)

        assert resolved.func == views.log_in

    def test_logout_url_resolves(self):
        """Test logout URL resolves to correct view"""
        from authentication import views

        url = reverse('logout')
        resolved = resolve(url)

        assert resolved.func == views.log_out

    def test_set_password_url_resolves(self):
        """Test set-password URL resolves to correct view"""
        from authentication import views

        url = reverse('set-password')
        resolved = resolve(url)

        assert resolved.func == views.set_password

    def test_change_password_url_resolves(self):
        """Test change-password URL resolves to correct view"""
        from authentication import views

        url = reverse('change-password')
        resolved = resolve(url)

        assert resolved.func == views.change_password

    def test_forgot_password_url_resolves(self):
        """Test forgot-password URL resolves to correct view"""
        from authentication import views

        url = reverse('forgot-password')
        resolved = resolve(url)

        assert resolved.func == views.forgot_password

    def test_reset_password_url_resolves(self):
        """Test reset-password URL resolves to correct view"""
        from authentication import views

        url = reverse('reset-password', kwargs={'uidb64': 'test123', 'token': 'testtoken'})
        resolved = resolve(url)

        assert resolved.func == views.reset_password


class TestAuthenticationUrlPatterns(BaseAPITestNoDatabase):
    """Test URL patterns structure"""

    def test_login_url_pattern(self):
        """Test login URL pattern"""
        url = reverse('login')
        assert url == '/auth/login'

    def test_logout_url_pattern(self):
        """Test logout URL pattern"""
        url = reverse('logout')
        assert url == '/auth/logout'

    def test_set_password_url_pattern(self):
        """Test set-password URL pattern"""
        url = reverse('set-password')
        assert url == '/auth/set_password'

    def test_change_password_url_pattern(self):
        """Test change-password URL pattern"""
        url = reverse('change-password')
        assert url == '/auth/change_password'

    def test_forgot_password_url_pattern(self):
        """Test forgot-password URL pattern"""
        url = reverse('forgot-password')
        assert url == '/auth/forgot_password'

    def test_reset_password_url_pattern(self):
        """Test reset-password URL pattern with parameters"""
        url = reverse('reset-password', kwargs={'uidb64': 'abc123', 'token': 'xyz789'})
        assert url == '/auth/reset_password/abc123/xyz789/'


class TestAuthenticationUrlReverse(BaseAPITestNoDatabase):
    """Test URL reverse functionality"""

    def test_login_url_reverse(self):
        """Test login URL can be reversed by name"""
        url = reverse('login')
        assert url is not None

    def test_logout_url_reverse(self):
        """Test logout URL can be reversed by name"""
        url = reverse('logout')
        assert url is not None

    def test_set_password_url_reverse(self):
        """Test set-password URL can be reversed by name"""
        url = reverse('set-password')
        assert url is not None

    def test_change_password_url_reverse(self):
        """Test change-password URL can be reversed by name"""
        url = reverse('change-password')
        assert url is not None

    def test_forgot_password_url_reverse(self):
        """Test forgot-password URL can be reversed by name"""
        url = reverse('forgot-password')
        assert url is not None

    def test_reset_password_url_reverse_with_kwargs(self):
        """Test reset-password URL can be reversed with kwargs"""
        url = reverse('reset-password', kwargs={'uidb64': 'test', 'token': 'token'})
        assert url is not None
        assert '/reset_password/test/token/' in url


class TestAuthenticationUrlNames(BaseAPITestNoDatabase):
    """Test URL names are correctly defined"""

    def test_login_url_name(self):
        """Test login URL name"""
        url = reverse('login')
        resolved = resolve(url)
        assert resolved.url_name == 'login'

    def test_logout_url_name(self):
        """Test logout URL name"""
        url = reverse('logout')
        resolved = resolve(url)
        assert resolved.url_name == 'logout'

    def test_set_password_url_name(self):
        """Test set-password URL name"""
        url = reverse('set-password')
        resolved = resolve(url)
        assert resolved.url_name == 'set-password'

    def test_change_password_url_name(self):
        """Test change-password URL name"""
        url = reverse('change-password')
        resolved = resolve(url)
        assert resolved.url_name == 'change-password'

    def test_forgot_password_url_name(self):
        """Test forgot-password URL name"""
        url = reverse('forgot-password')
        resolved = resolve(url)
        assert resolved.url_name == 'forgot-password'

    def test_reset_password_url_name(self):
        """Test reset-password URL name"""
        url = reverse('reset-password', kwargs={'uidb64': 'test', 'token': 'token'})
        resolved = resolve(url)
        assert resolved.url_name == 'reset-password'


class TestAuthenticationUrlParameters(BaseAPITestNoDatabase):
    """Test URL parameters are correctly parsed"""

    def test_reset_password_url_extracts_uidb64(self):
        """Test reset-password URL extracts uidb64 parameter"""
        url = '/auth/reset_password/abc123xyz/tokenvalue/'
        resolved = resolve(url)

        assert 'uidb64' in resolved.kwargs
        assert resolved.kwargs['uidb64'] == 'abc123xyz'

    def test_reset_password_url_extracts_token(self):
        """Test reset-password URL extracts token parameter"""
        url = '/auth/reset_password/abc123xyz/tokenvalue/'
        resolved = resolve(url)

        assert 'token' in resolved.kwargs
        assert resolved.kwargs['token'] == 'tokenvalue'

    def test_reset_password_url_with_different_values(self):
        """Test reset-password URL works with different parameter values"""
        test_cases = [
            ('uid1', 'token1'),
            ('uid2', 'token2'),
            ('uid3', 'token3'),
        ]

        for uidb64, token in test_cases:
            url = reverse('reset-password', kwargs={'uidb64': uidb64, 'token': token})
            resolved = resolve(url)
            assert resolved.kwargs['uidb64'] == uidb64
            assert resolved.kwargs['token'] == token
