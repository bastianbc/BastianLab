# tests/unit/samplelib/test_urls.py
"""
Samplelib URLs Test Cases - No Database Required
"""
import pytest
from django.urls import reverse, resolve
from tests.utils.base_test import BaseAPITestNoDatabase


class TestSamplelibUrls(BaseAPITestNoDatabase):
    """Test samplelib URL patterns"""

    def test_samplelibs_url_resolves(self):
        """Test samplelibs URL resolves to correct view"""
        from samplelib import views

        url = reverse('samplelibs')
        resolved = resolve(url)

        assert resolved.func == views.samplelibs

    def test_filter_samplelibs_url_resolves(self):
        """Test filter-samplelibs URL resolves to correct view"""
        from samplelib import views

        url = reverse('filter-samplelibs')
        resolved = resolve(url)

        assert resolved.func == views.filter_samplelibs

    def test_new_samplelib_url_resolves(self):
        """Test new-samplelib URL resolves to correct view"""
        from samplelib import views

        url = reverse('new-samplelib')
        resolved = resolve(url)

        assert resolved.func == views.new_samplelib

    def test_new_samplelib_async_url_resolves(self):
        """Test new-samplelib-async URL resolves to correct view"""
        from samplelib import views

        url = reverse('new-samplelib-async')
        resolved = resolve(url)

        assert resolved.func == views.new_samplelib_async

    def test_edit_samplelib_url_resolves(self):
        """Test edit-samplelib URL resolves to correct view"""
        from samplelib import views

        url = reverse('edit-samplelib', args=['test123'])
        resolved = resolve(url)

        assert resolved.func == views.edit_samplelib

    def test_edit_samplelib_async_url_resolves(self):
        """Test edit-samplelib-async URL resolves to correct view"""
        from samplelib import views

        url = reverse('edit-samplelib-async')
        resolved = resolve(url)

        assert resolved.func == views.edit_samplelib_async

    def test_delete_samplelib_url_resolves(self):
        """Test delete-samplelib URL resolves to correct view"""
        from samplelib import views

        url = reverse('delete-samplelib', args=['test123'])
        resolved = resolve(url)

        assert resolved.func == views.delete_samplelib

    def test_delete_batch_samplelibs_url_resolves(self):
        """Test delete-batch-samplelibs URL resolves to correct view"""
        from samplelib import views

        url = reverse('delete-batch-samplelibs')
        resolved = resolve(url)

        assert resolved.func == views.delete_batch_samplelibs

    def test_get_used_nucacids_url_resolves(self):
        """Test get-used-nucacids URL resolves to correct view"""
        from samplelib import views

        url = reverse('get-used-nucacids', args=[1])
        resolved = resolve(url)

        assert resolved.func == views.get_used_nucacids

    def test_update_async_url_resolves(self):
        """Test update-async URL resolves to correct view"""
        from samplelib import views

        url = reverse('update-async')
        resolved = resolve(url)

        assert resolved.func == views.update_sl_na_link_async


class TestSamplelibUrlPatterns(BaseAPITestNoDatabase):
    """Test URL patterns structure"""

    def test_samplelibs_url_pattern(self):
        """Test samplelibs URL pattern"""
        url = reverse('samplelibs')
        assert url == '/samplelib/'

    def test_filter_samplelibs_url_pattern(self):
        """Test filter-samplelibs URL pattern"""
        url = reverse('filter-samplelibs')
        assert url == '/samplelib/filter_samplelibs'

    def test_new_samplelib_url_pattern(self):
        """Test new-samplelib URL pattern"""
        url = reverse('new-samplelib')
        assert url == '/samplelib/new'

    def test_edit_samplelib_url_pattern(self):
        """Test edit-samplelib URL pattern with ID"""
        url = reverse('edit-samplelib', args=['testid'])
        assert url == '/samplelib/edit/testid'

    def test_delete_samplelib_url_pattern(self):
        """Test delete-samplelib URL pattern with ID"""
        url = reverse('delete-samplelib', args=['testid'])
        assert url == '/samplelib/delete/testid'

    def test_get_used_nucacids_url_pattern(self):
        """Test get-used-nucacids URL pattern with ID"""
        url = reverse('get-used-nucacids', args=[1])
        assert url == '/samplelib/1/used_nucacids'


class TestSamplelibUrlReverse(BaseAPITestNoDatabase):
    """Test URL reverse functionality"""

    def test_samplelibs_url_reverse(self):
        """Test samplelibs URL can be reversed by name"""
        url = reverse('samplelibs')
        assert url is not None

    def test_filter_samplelibs_url_reverse(self):
        """Test filter-samplelibs URL can be reversed by name"""
        url = reverse('filter-samplelibs')
        assert url is not None

    def test_new_samplelib_url_reverse(self):
        """Test new-samplelib URL can be reversed by name"""
        url = reverse('new-samplelib')
        assert url is not None

    def test_edit_samplelib_url_reverse_with_args(self):
        """Test edit-samplelib URL can be reversed with args"""
        url = reverse('edit-samplelib', args=['testid'])
        assert url is not None
        assert '/edit/testid' in url

    def test_delete_samplelib_url_reverse_with_args(self):
        """Test delete-samplelib URL can be reversed with args"""
        url = reverse('delete-samplelib', args=['testid'])
        assert url is not None
        assert '/delete/testid' in url


class TestSamplelibUrlNames(BaseAPITestNoDatabase):
    """Test URL names are correctly defined"""

    def test_samplelibs_url_name(self):
        """Test samplelibs URL name"""
        url = reverse('samplelibs')
        resolved = resolve(url)
        assert resolved.url_name == 'samplelibs'

    def test_filter_samplelibs_url_name(self):
        """Test filter-samplelibs URL name"""
        url = reverse('filter-samplelibs')
        resolved = resolve(url)
        assert resolved.url_name == 'filter-samplelibs'

    def test_new_samplelib_url_name(self):
        """Test new-samplelib URL name"""
        url = reverse('new-samplelib')
        resolved = resolve(url)
        assert resolved.url_name == 'new-samplelib'

    def test_edit_samplelib_url_name(self):
        """Test edit-samplelib URL name"""
        url = reverse('edit-samplelib', args=['testid'])
        resolved = resolve(url)
        assert resolved.url_name == 'edit-samplelib'

    def test_delete_samplelib_url_name(self):
        """Test delete-samplelib URL name"""
        url = reverse('delete-samplelib', args=['testid'])
        resolved = resolve(url)
        assert resolved.url_name == 'delete-samplelib'


class TestSamplelibUrlParameters(BaseAPITestNoDatabase):
    """Test URL parameters are correctly parsed"""

    def test_edit_samplelib_url_extracts_id(self):
        """Test edit-samplelib URL extracts id parameter"""
        url = '/samplelib/edit/test123'
        resolved = resolve(url)

        assert 'id' in resolved.kwargs
        assert resolved.kwargs['id'] == 'test123'

    def test_delete_samplelib_url_extracts_id(self):
        """Test delete-samplelib URL extracts id parameter"""
        url = '/samplelib/delete/test456'
        resolved = resolve(url)

        assert 'id' in resolved.kwargs
        assert resolved.kwargs['id'] == 'test456'

    def test_get_used_nucacids_url_extracts_id(self):
        """Test get-used-nucacids URL extracts id parameter"""
        url = '/samplelib/42/used_nucacids'
        resolved = resolve(url)

        assert 'id' in resolved.kwargs
        assert resolved.kwargs['id'] == 42

    def test_edit_samplelib_url_with_different_ids(self):
        """Test edit-samplelib URL works with different IDs"""
        for test_id in ['id1', 'id2', 'id3']:
            url = reverse('edit-samplelib', args=[test_id])
            resolved = resolve(url)
            assert resolved.kwargs['id'] == test_id

    def test_delete_samplelib_url_with_different_ids(self):
        """Test delete-samplelib URL works with different IDs"""
        for test_id in ['del1', 'del2', 'del3']:
            url = reverse('delete-samplelib', args=[test_id])
            resolved = resolve(url)
            assert resolved.kwargs['id'] == test_id
