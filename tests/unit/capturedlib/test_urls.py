# tests/unit/capturedlib/test_urls.py
"""
Capturedlib URLs Test Cases - No Database Required
"""
import pytest
from django.urls import reverse, resolve
from tests.utils.base_test import BaseAPITestNoDatabase


class TestCapturedlibUrls(BaseAPITestNoDatabase):
    """Test capturedlib URL patterns"""

    def test_capturedlibs_url_resolves(self):
        """Test capturedlibs URL resolves to correct view"""
        from capturedlib import views

        url = reverse('capturedlibs')
        resolved = resolve(url)

        assert resolved.func == views.capturedlibs

    def test_filter_capturedlibs_url_resolves(self):
        """Test filter-capturedlibs URL resolves to correct view"""
        from capturedlib import views

        url = reverse('filter-capturedlibs')
        resolved = resolve(url)

        assert resolved.func == views.filter_capturedlibs

    def test_edit_capturedlib_async_url_resolves(self):
        """Test edit-capturedlib-async URL resolves to correct view"""
        from capturedlib import views

        url = reverse('edit-capturedlib-async')
        resolved = resolve(url)

        assert resolved.func == views.edit_capturedlib_async

    def test_new_capturedlib_url_resolves(self):
        """Test new-capturedlib URL resolves to correct view"""
        from capturedlib import views

        url = reverse('new-capturedlib')
        resolved = resolve(url)

        assert resolved.func == views.new_capturedlib

    def test_new_capturedlib_async_url_resolves(self):
        """Test new-capturedlib-async URL resolves to correct view"""
        from capturedlib import views

        url = reverse('new-capturedlib-async')
        resolved = resolve(url)

        assert resolved.func == views.new_capturedlib_async

    def test_edit_capturedlib_url_resolves(self):
        """Test edit-capturedlib URL resolves to correct view"""
        from capturedlib import views

        url = reverse('edit-capturedlib', args=['test123'])
        resolved = resolve(url)

        assert resolved.func == views.edit_capturedlib

    def test_delete_capturedlib_url_resolves(self):
        """Test delete-capturedlib URL resolves to correct view"""
        from capturedlib import views

        url = reverse('delete-capturedlib', args=['test123'])
        resolved = resolve(url)

        assert resolved.func == views.delete_capturedlib

    def test_delete_batch_capturedlibs_url_resolves(self):
        """Test delete-batch-capturedlibs URL resolves to correct view"""
        from capturedlib import views

        url = reverse('delete-batch-capturedlibs')
        resolved = resolve(url)

        assert resolved.func == views.delete_batch_capturedlibs

    def test_get_used_samplelibs_url_resolves(self):
        """Test get-used-samplelibs URL resolves to correct view"""
        from capturedlib import views

        url = reverse('get-used-samplelibs', args=[1])
        resolved = resolve(url)

        assert resolved.func == views.get_used_samplelibs

    def test_update_async_url_resolves(self):
        """Test update_async URL resolves to correct view"""
        from capturedlib import views

        url = reverse('update_async', args=[1])
        resolved = resolve(url)

        assert resolved.func == views.update_async

    def test_check_identical_barcode_url_resolves(self):
        """Test check-identical-barcode URL resolves to correct view"""
        from capturedlib import views

        url = reverse('check-identical-barcode')
        resolved = resolve(url)

        assert resolved.func == views.check_idendical_barcode


class TestCapturedlibUrlPatterns(BaseAPITestNoDatabase):
    """Test URL patterns structure"""

    def test_capturedlibs_url_pattern(self):
        """Test capturedlibs URL pattern"""
        url = reverse('capturedlibs')
        assert url == '/capturedlib/'

    def test_filter_capturedlibs_url_pattern(self):
        """Test filter-capturedlibs URL pattern"""
        url = reverse('filter-capturedlibs')
        assert url == '/capturedlib/filter_capturedlibs'

    def test_new_capturedlib_url_pattern(self):
        """Test new-capturedlib URL pattern"""
        url = reverse('new-capturedlib')
        assert url == '/capturedlib/new'

    def test_new_capturedlib_async_url_pattern(self):
        """Test new-capturedlib-async URL pattern"""
        url = reverse('new-capturedlib-async')
        assert url == '/capturedlib/new_async'

    def test_edit_capturedlib_url_pattern(self):
        """Test edit-capturedlib URL pattern with ID"""
        url = reverse('edit-capturedlib', args=['testid'])
        assert url == '/capturedlib/edit/testid'

    def test_delete_capturedlib_url_pattern(self):
        """Test delete-capturedlib URL pattern with ID"""
        url = reverse('delete-capturedlib', args=['testid'])
        assert url == '/capturedlib/delete/testid'

    def test_get_used_samplelibs_url_pattern(self):
        """Test get-used-samplelibs URL pattern with ID"""
        url = reverse('get-used-samplelibs', args=[1])
        assert url == '/capturedlib/1/used_samplelibs'

    def test_update_async_url_pattern(self):
        """Test update_async URL pattern with ID"""
        url = reverse('update_async', args=[1])
        assert url == '/capturedlib/1/update_async'


class TestCapturedlibUrlReverse(BaseAPITestNoDatabase):
    """Test URL reverse functionality"""

    def test_capturedlibs_url_reverse(self):
        """Test capturedlibs URL can be reversed by name"""
        url = reverse('capturedlibs')
        assert url is not None

    def test_filter_capturedlibs_url_reverse(self):
        """Test filter-capturedlibs URL can be reversed by name"""
        url = reverse('filter-capturedlibs')
        assert url is not None

    def test_new_capturedlib_url_reverse(self):
        """Test new-capturedlib URL can be reversed by name"""
        url = reverse('new-capturedlib')
        assert url is not None

    def test_edit_capturedlib_url_reverse_with_args(self):
        """Test edit-capturedlib URL can be reversed with args"""
        url = reverse('edit-capturedlib', args=['testid'])
        assert url is not None
        assert '/edit/testid' in url

    def test_delete_capturedlib_url_reverse_with_args(self):
        """Test delete-capturedlib URL can be reversed with args"""
        url = reverse('delete-capturedlib', args=['testid'])
        assert url is not None
        assert '/delete/testid' in url


class TestCapturedlibUrlNames(BaseAPITestNoDatabase):
    """Test URL names are correctly defined"""

    def test_capturedlibs_url_name(self):
        """Test capturedlibs URL name"""
        url = reverse('capturedlibs')
        resolved = resolve(url)
        assert resolved.url_name == 'capturedlibs'

    def test_filter_capturedlibs_url_name(self):
        """Test filter-capturedlibs URL name"""
        url = reverse('filter-capturedlibs')
        resolved = resolve(url)
        assert resolved.url_name == 'filter-capturedlibs'

    def test_new_capturedlib_url_name(self):
        """Test new-capturedlib URL name"""
        url = reverse('new-capturedlib')
        resolved = resolve(url)
        assert resolved.url_name == 'new-capturedlib'

    def test_edit_capturedlib_url_name(self):
        """Test edit-capturedlib URL name"""
        url = reverse('edit-capturedlib', args=['testid'])
        resolved = resolve(url)
        assert resolved.url_name == 'edit-capturedlib'

    def test_delete_capturedlib_url_name(self):
        """Test delete-capturedlib URL name"""
        url = reverse('delete-capturedlib', args=['testid'])
        resolved = resolve(url)
        assert resolved.url_name == 'delete-capturedlib'


class TestCapturedlibUrlParameters(BaseAPITestNoDatabase):
    """Test URL parameters are correctly parsed"""

    def test_edit_capturedlib_url_extracts_id(self):
        """Test edit-capturedlib URL extracts id parameter"""
        url = '/capturedlib/edit/test123'
        resolved = resolve(url)

        assert 'id' in resolved.kwargs
        assert resolved.kwargs['id'] == 'test123'

    def test_delete_capturedlib_url_extracts_id(self):
        """Test delete-capturedlib URL extracts id parameter"""
        url = '/capturedlib/delete/test456'
        resolved = resolve(url)

        assert 'id' in resolved.kwargs
        assert resolved.kwargs['id'] == 'test456'

    def test_get_used_samplelibs_url_extracts_id(self):
        """Test get-used-samplelibs URL extracts id parameter"""
        url = '/capturedlib/42/used_samplelibs'
        resolved = resolve(url)

        assert 'id' in resolved.kwargs
        assert resolved.kwargs['id'] == 42

    def test_update_async_url_extracts_id(self):
        """Test update_async URL extracts id parameter"""
        url = '/capturedlib/42/update_async'
        resolved = resolve(url)

        assert 'id' in resolved.kwargs
        assert resolved.kwargs['id'] == 42

    def test_edit_capturedlib_url_with_different_ids(self):
        """Test edit-capturedlib URL works with different IDs"""
        for test_id in ['id1', 'id2', 'id3']:
            url = reverse('edit-capturedlib', args=[test_id])
            resolved = resolve(url)
            assert resolved.kwargs['id'] == test_id

    def test_delete_capturedlib_url_with_different_ids(self):
        """Test delete-capturedlib URL works with different IDs"""
        for test_id in ['del1', 'del2', 'del3']:
            url = reverse('delete-capturedlib', args=[test_id])
            resolved = resolve(url)
            assert resolved.kwargs['id'] == test_id
