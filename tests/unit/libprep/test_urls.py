# tests/unit/libprep/test_urls.py
"""
Libprep URLs Test Cases - No Database Required
"""
import pytest
from django.urls import reverse, resolve
from tests.utils.base_test import BaseAPITestNoDatabase


class TestLibprepUrls(BaseAPITestNoDatabase):
    """Test libprep URL patterns"""

    def test_nucacids_url_resolves(self):
        """Test nucacids URL resolves to correct view"""
        from libprep import views

        url = reverse('nucacids')
        resolved = resolve(url)

        assert resolved.func == views.nucacids

    def test_filter_nucacids_url_resolves(self):
        """Test filter-nucacids URL resolves to correct view"""
        from libprep import views

        url = reverse('filter-nucacids')
        resolved = resolve(url)

        assert resolved.func == views.filter_nucacids

    def test_new_nucacid_url_resolves(self):
        """Test new-nucacid URL resolves to correct view"""
        from libprep import views

        url = reverse('new-nucacid')
        resolved = resolve(url)

        assert resolved.func == views.new_nucacid

    def test_new_nucacid_async_url_resolves(self):
        """Test new-nucacid-async URL resolves to correct view"""
        from libprep import views

        url = reverse('new-nucacid-async')
        resolved = resolve(url)

        assert resolved.func == views.new_nucacid_async

    def test_edit_nucacid_url_resolves(self):
        """Test edit-nucacid URL resolves to correct view"""
        from libprep import views

        url = reverse('edit-nucacid', args=['test123'])
        resolved = resolve(url)

        assert resolved.func == views.edit_nucacid

    def test_edit_nucacid_async_url_resolves(self):
        """Test edit-nucacid-async URL resolves to correct view"""
        from libprep import views

        url = reverse('edit-nucacid-async')
        resolved = resolve(url)

        assert resolved.func == views.edit_nucacid_async

    def test_delete_nucacid_url_resolves(self):
        """Test delete-nucacid URL resolves to correct view"""
        from libprep import views

        url = reverse('delete-nucacid', args=['test123'])
        resolved = resolve(url)

        assert resolved.func == views.delete_nucacid

    def test_delete_batch_nucacids_url_resolves(self):
        """Test delete-batch-nucacids URL resolves to correct view"""
        from libprep import views

        url = reverse('delete-batch-nucacids')
        resolved = resolve(url)

        assert resolved.func == views.delete_batch_nucacids

    def test_get_na_types_url_resolves(self):
        """Test get-na-types URL resolves to correct view"""
        from libprep import views

        url = reverse('get-na-types')
        resolved = resolve(url)

        assert resolved.func == views.get_na_types


class TestLibprepUrlPatterns(BaseAPITestNoDatabase):
    """Test URL patterns structure"""

    def test_nucacids_url_pattern(self):
        """Test nucacids URL pattern"""
        url = reverse('nucacids')
        assert url == '/libprep/'

    def test_filter_nucacids_url_pattern(self):
        """Test filter-nucacids URL pattern"""
        url = reverse('filter-nucacids')
        assert url == '/libprep/filter_nucacids'

    def test_new_nucacid_url_pattern(self):
        """Test new-nucacid URL pattern"""
        url = reverse('new-nucacid')
        assert url == '/libprep/new'

    def test_new_nucacid_async_url_pattern(self):
        """Test new-nucacid-async URL pattern"""
        url = reverse('new-nucacid-async')
        assert url == '/libprep/new_async'

    def test_edit_nucacid_url_pattern(self):
        """Test edit-nucacid URL pattern with ID"""
        url = reverse('edit-nucacid', args=['testid'])
        assert url == '/libprep/edit/testid'

    def test_delete_nucacid_url_pattern(self):
        """Test delete-nucacid URL pattern with ID"""
        url = reverse('delete-nucacid', args=['testid'])
        assert url == '/libprep/delete/testid'


class TestLibprepUrlReverse(BaseAPITestNoDatabase):
    """Test URL reverse functionality"""

    def test_nucacids_url_reverse(self):
        """Test nucacids URL can be reversed by name"""
        url = reverse('nucacids')
        assert url is not None

    def test_filter_nucacids_url_reverse(self):
        """Test filter-nucacids URL can be reversed by name"""
        url = reverse('filter-nucacids')
        assert url is not None

    def test_new_nucacid_url_reverse(self):
        """Test new-nucacid URL can be reversed by name"""
        url = reverse('new-nucacid')
        assert url is not None

    def test_new_nucacid_async_url_reverse(self):
        """Test new-nucacid-async URL can be reversed by name"""
        url = reverse('new-nucacid-async')
        assert url is not None

    def test_edit_nucacid_url_reverse_with_args(self):
        """Test edit-nucacid URL can be reversed with args"""
        url = reverse('edit-nucacid', args=['testid'])
        assert url is not None
        assert '/edit/testid' in url

    def test_delete_nucacid_url_reverse_with_args(self):
        """Test delete-nucacid URL can be reversed with args"""
        url = reverse('delete-nucacid', args=['testid'])
        assert url is not None
        assert '/delete/testid' in url


class TestLibprepUrlNames(BaseAPITestNoDatabase):
    """Test URL names are correctly defined"""

    def test_nucacids_url_name(self):
        """Test nucacids URL name"""
        url = reverse('nucacids')
        resolved = resolve(url)
        assert resolved.url_name == 'nucacids'

    def test_filter_nucacids_url_name(self):
        """Test filter-nucacids URL name"""
        url = reverse('filter-nucacids')
        resolved = resolve(url)
        assert resolved.url_name == 'filter-nucacids'

    def test_new_nucacid_url_name(self):
        """Test new-nucacid URL name"""
        url = reverse('new-nucacid')
        resolved = resolve(url)
        assert resolved.url_name == 'new-nucacid'

    def test_new_nucacid_async_url_name(self):
        """Test new-nucacid-async URL name"""
        url = reverse('new-nucacid-async')
        resolved = resolve(url)
        assert resolved.url_name == 'new-nucacid-async'

    def test_edit_nucacid_url_name(self):
        """Test edit-nucacid URL name"""
        url = reverse('edit-nucacid', args=['testid'])
        resolved = resolve(url)
        assert resolved.url_name == 'edit-nucacid'

    def test_delete_nucacid_url_name(self):
        """Test delete-nucacid URL name"""
        url = reverse('delete-nucacid', args=['testid'])
        resolved = resolve(url)
        assert resolved.url_name == 'delete-nucacid'


class TestLibprepUrlParameters(BaseAPITestNoDatabase):
    """Test URL parameters are correctly parsed"""

    def test_edit_nucacid_url_extracts_id(self):
        """Test edit-nucacid URL extracts id parameter"""
        url = '/libprep/edit/test123'
        resolved = resolve(url)

        assert 'id' in resolved.kwargs
        assert resolved.kwargs['id'] == 'test123'

    def test_delete_nucacid_url_extracts_id(self):
        """Test delete-nucacid URL extracts id parameter"""
        url = '/libprep/delete/test456'
        resolved = resolve(url)

        assert 'id' in resolved.kwargs
        assert resolved.kwargs['id'] == 'test456'

    def test_edit_nucacid_url_with_different_ids(self):
        """Test edit-nucacid URL works with different IDs"""
        for test_id in ['id1', 'id2', 'id3']:
            url = reverse('edit-nucacid', args=[test_id])
            resolved = resolve(url)
            assert resolved.kwargs['id'] == test_id

    def test_delete_nucacid_url_with_different_ids(self):
        """Test delete-nucacid URL works with different IDs"""
        for test_id in ['del1', 'del2', 'del3']:
            url = reverse('delete-nucacid', args=[test_id])
            resolved = resolve(url)
            assert resolved.kwargs['id'] == test_id
