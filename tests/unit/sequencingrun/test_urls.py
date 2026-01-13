# tests/unit/sequencingrun/test_urls.py
"""
Sequencingrun URLs Test Cases - No Database Required
"""
import pytest
from django.urls import reverse, resolve
from tests.utils.base_test import BaseAPITestNoDatabase


class TestSequencingrunUrls(BaseAPITestNoDatabase):
    """Test sequencingrun URL patterns"""

    def test_sequencingruns_url_resolves(self):
        """Test sequencingruns URL resolves to correct view"""
        from sequencingrun import views

        url = reverse('sequencingruns')
        resolved = resolve(url)

        assert resolved.func == views.sequencingruns

    def test_filter_sequencingruns_url_resolves(self):
        """Test filter-sequencingruns URL resolves to correct view"""
        from sequencingrun import views

        url = reverse('filter-sequencingruns')
        resolved = resolve(url)

        assert resolved.func == views.filter_sequencingruns

    def test_edit_sequencingrun_async_url_resolves(self):
        """Test edit-sequencingrun-async URL resolves to correct view"""
        from sequencingrun import views

        url = reverse('edit-sequencingrun-async')
        resolved = resolve(url)

        assert resolved.func == views.edit_sequencingrun_async

    def test_new_sequencingrun_url_resolves(self):
        """Test new-sequencingrun URL resolves to correct view"""
        from sequencingrun import views

        url = reverse('new-sequencingrun')
        resolved = resolve(url)

        assert resolved.func == views.new_sequencingrun

    def test_new_sequencingrun_async_url_resolves(self):
        """Test new-sequencingrun-async URL resolves to correct view"""
        from sequencingrun import views

        url = reverse('new-sequencingrun-async')
        resolved = resolve(url)

        assert resolved.func == views.new_sequencingrun_async

    def test_edit_sequencingrun_url_resolves(self):
        """Test edit-sequencingrun URL resolves to correct view"""
        from sequencingrun import views

        url = reverse('edit-sequencingrun', args=['test123'])
        resolved = resolve(url)

        assert resolved.func == views.edit_sequencingrun

    def test_delete_sequencingrun_url_resolves(self):
        """Test delete-sequencingrun URL resolves to correct view"""
        from sequencingrun import views

        url = reverse('delete-sequencingrun', args=['test123'])
        resolved = resolve(url)

        assert resolved.func == views.delete_sequencingrun

    def test_delete_batch_sequencingruns_url_resolves(self):
        """Test delete-batch-sequencingruns URL resolves to correct view"""
        from sequencingrun import views

        url = reverse('delete-batch-sequencingruns')
        resolved = resolve(url)

        assert resolved.func == views.delete_batch_sequencingruns

    def test_get_used_sequencinglibs_url_resolves(self):
        """Test get-used-sequencinglibs URL resolves to correct view"""
        from sequencingrun import views

        url = reverse('get-used-sequencinglibs', args=[1])
        resolved = resolve(url)

        assert resolved.func == views.get_used_sequencinglibs

    def test_get_facilities_url_resolves(self):
        """Test get-facilities URL resolves to correct view"""
        from sequencingrun import views

        url = reverse('get-facilities')
        resolved = resolve(url)

        assert resolved.func == views.get_facilities

    def test_get_sequencers_url_resolves(self):
        """Test get-sequencers URL resolves to correct view"""
        from sequencingrun import views

        url = reverse('get-sequencers')
        resolved = resolve(url)

        assert resolved.func == views.get_sequencers

    def test_get_pes_url_resolves(self):
        """Test get-pes URL resolves to correct view"""
        from sequencingrun import views

        url = reverse('get-pes')
        resolved = resolve(url)

        assert resolved.func == views.get_pes


class TestSequencingrunUrlPatterns(BaseAPITestNoDatabase):
    """Test URL patterns structure"""

    def test_sequencingruns_url_pattern(self):
        """Test sequencingruns URL pattern"""
        url = reverse('sequencingruns')
        assert url == '/sequencingrun/'

    def test_filter_sequencingruns_url_pattern(self):
        """Test filter-sequencingruns URL pattern"""
        url = reverse('filter-sequencingruns')
        assert url == '/sequencingrun/filter_sequencingruns'

    def test_new_sequencingrun_url_pattern(self):
        """Test new-sequencingrun URL pattern"""
        url = reverse('new-sequencingrun')
        assert url == '/sequencingrun/new'

    def test_edit_sequencingrun_url_pattern(self):
        """Test edit-sequencingrun URL pattern with ID"""
        url = reverse('edit-sequencingrun', args=['testid'])
        assert url == '/sequencingrun/edit/testid'

    def test_delete_sequencingrun_url_pattern(self):
        """Test delete-sequencingrun URL pattern with ID"""
        url = reverse('delete-sequencingrun', args=['testid'])
        assert url == '/sequencingrun/delete/testid'

    def test_get_used_sequencinglibs_url_pattern(self):
        """Test get-used-sequencinglibs URL pattern with ID"""
        url = reverse('get-used-sequencinglibs', args=[1])
        assert url == '/sequencingrun/1/used_sequencinglibs'


class TestSequencingrunUrlReverse(BaseAPITestNoDatabase):
    """Test URL reverse functionality"""

    def test_sequencingruns_url_reverse(self):
        """Test sequencingruns URL can be reversed by name"""
        url = reverse('sequencingruns')
        assert url is not None

    def test_filter_sequencingruns_url_reverse(self):
        """Test filter-sequencingruns URL can be reversed by name"""
        url = reverse('filter-sequencingruns')
        assert url is not None

    def test_new_sequencingrun_url_reverse(self):
        """Test new-sequencingrun URL can be reversed by name"""
        url = reverse('new-sequencingrun')
        assert url is not None

    def test_edit_sequencingrun_url_reverse_with_args(self):
        """Test edit-sequencingrun URL can be reversed with args"""
        url = reverse('edit-sequencingrun', args=['testid'])
        assert url is not None
        assert '/edit/testid' in url

    def test_delete_sequencingrun_url_reverse_with_args(self):
        """Test delete-sequencingrun URL can be reversed with args"""
        url = reverse('delete-sequencingrun', args=['testid'])
        assert url is not None
        assert '/delete/testid' in url


class TestSequencingrunUrlNames(BaseAPITestNoDatabase):
    """Test URL names are correctly defined"""

    def test_sequencingruns_url_name(self):
        """Test sequencingruns URL name"""
        url = reverse('sequencingruns')
        resolved = resolve(url)
        assert resolved.url_name == 'sequencingruns'

    def test_filter_sequencingruns_url_name(self):
        """Test filter-sequencingruns URL name"""
        url = reverse('filter-sequencingruns')
        resolved = resolve(url)
        assert resolved.url_name == 'filter-sequencingruns'

    def test_new_sequencingrun_url_name(self):
        """Test new-sequencingrun URL name"""
        url = reverse('new-sequencingrun')
        resolved = resolve(url)
        assert resolved.url_name == 'new-sequencingrun'

    def test_edit_sequencingrun_url_name(self):
        """Test edit-sequencingrun URL name"""
        url = reverse('edit-sequencingrun', args=['testid'])
        resolved = resolve(url)
        assert resolved.url_name == 'edit-sequencingrun'

    def test_delete_sequencingrun_url_name(self):
        """Test delete-sequencingrun URL name"""
        url = reverse('delete-sequencingrun', args=['testid'])
        resolved = resolve(url)
        assert resolved.url_name == 'delete-sequencingrun'


class TestSequencingrunUrlParameters(BaseAPITestNoDatabase):
    """Test URL parameters are correctly parsed"""

    def test_edit_sequencingrun_url_extracts_id(self):
        """Test edit-sequencingrun URL extracts id parameter"""
        url = '/sequencingrun/edit/test123'
        resolved = resolve(url)

        assert 'id' in resolved.kwargs
        assert resolved.kwargs['id'] == 'test123'

    def test_delete_sequencingrun_url_extracts_id(self):
        """Test delete-sequencingrun URL extracts id parameter"""
        url = '/sequencingrun/delete/test456'
        resolved = resolve(url)

        assert 'id' in resolved.kwargs
        assert resolved.kwargs['id'] == 'test456'

    def test_get_used_sequencinglibs_url_extracts_id(self):
        """Test get-used-sequencinglibs URL extracts id parameter"""
        url = '/sequencingrun/42/used_sequencinglibs'
        resolved = resolve(url)

        assert 'id' in resolved.kwargs
        assert resolved.kwargs['id'] == 42

    def test_edit_sequencingrun_url_with_different_ids(self):
        """Test edit-sequencingrun URL works with different IDs"""
        for test_id in ['id1', 'id2', 'id3']:
            url = reverse('edit-sequencingrun', args=[test_id])
            resolved = resolve(url)
            assert resolved.kwargs['id'] == test_id

    def test_delete_sequencingrun_url_with_different_ids(self):
        """Test delete-sequencingrun URL works with different IDs"""
        for test_id in ['del1', 'del2', 'del3']:
            url = reverse('delete-sequencingrun', args=[test_id])
            resolved = resolve(url)
            assert resolved.kwargs['id'] == test_id
