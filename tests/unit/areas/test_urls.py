# tests/unit/areas/test_urls.py
"""
Areas URLs Test Cases - No Database Required
"""
import pytest
from django.urls import reverse, resolve
from tests.utils.base_test import BaseAPITestNoDatabase


class TestAreasUrls(BaseAPITestNoDatabase):
    """Test areas URL patterns"""

    def test_areas_url_resolves(self):
        """Test areas URL resolves to correct view"""
        from areas import views

        url = reverse('areas')
        resolved = resolve(url)

        assert resolved.func == views.areas

    def test_filter_areas_url_resolves(self):
        """Test filter-areas URL resolves to correct view"""
        from areas import views

        url = reverse('filter-areas')
        resolved = resolve(url)

        assert resolved.func == views.filter_areas

    def test_new_area_url_resolves(self):
        """Test new-area URL resolves to correct view"""
        from areas import views

        url = reverse('new-area')
        resolved = resolve(url)

        assert resolved.func == views.new_area

    def test_add_area_to_block_async_url_resolves(self):
        """Test add-area-to-block-async URL resolves to correct view"""
        from areas import views

        url = reverse('add-area-to-block-async')
        resolved = resolve(url)

        assert resolved.func == views.add_area_to_block_async

    def test_edit_area_url_resolves(self):
        """Test edit-area URL resolves to correct view"""
        from areas import views

        url = reverse('edit-area', args=['test123'])
        resolved = resolve(url)

        assert resolved.func == views.edit_area

    def test_edit_area_async_url_resolves(self):
        """Test edit-area-async URL resolves to correct view"""
        from areas import views

        url = reverse('edit-area-async')
        resolved = resolve(url)

        assert resolved.func == views.edit_area_async

    def test_delete_area_url_resolves(self):
        """Test delete-area URL resolves to correct view"""
        from areas import views

        url = reverse('delete-area', args=['test123'])
        resolved = resolve(url)

        assert resolved.func == views.delete_area

    def test_delete_batch_areas_url_resolves(self):
        """Test delete-batch-areas URL resolves to correct view"""
        from areas import views

        url = reverse('delete-batch-areas')
        resolved = resolve(url)

        assert resolved.func == views.delete_batch_areas

    def test_get_collections_url_resolves(self):
        """Test get-collections URL resolves to correct view"""
        from areas import views

        url = reverse('get-collections')
        resolved = resolve(url)

        assert resolved.func == views.get_collections

    def test_get_area_types_url_resolves(self):
        """Test get-area-types URL resolves to correct view"""
        from areas import views

        url = reverse('get-area-types')
        resolved = resolve(url)

        assert resolved.func == views.get_area_types

    def test_get_block_async_by_area_url_resolves(self):
        """Test get-block-async-by-area URL resolves to correct view"""
        from areas import views

        url = reverse('get-block-async-by-area', args=[1])
        resolved = resolve(url)

        assert resolved.func == views.get_block_async_by_area


class TestAreasUrlPatterns(BaseAPITestNoDatabase):
    """Test URL patterns structure"""

    def test_areas_url_pattern(self):
        """Test areas URL pattern"""
        url = reverse('areas')
        assert url == '/areas/'

    def test_filter_areas_url_pattern(self):
        """Test filter-areas URL pattern"""
        url = reverse('filter-areas')
        assert url == '/areas/filter_areas'

    def test_new_area_url_pattern(self):
        """Test new-area URL pattern"""
        url = reverse('new-area')
        assert url == '/areas/new'

    def test_edit_area_url_pattern(self):
        """Test edit-area URL pattern with ID"""
        url = reverse('edit-area', args=['testid'])
        assert url == '/areas/edit/testid'

    def test_delete_area_url_pattern(self):
        """Test delete-area URL pattern with ID"""
        url = reverse('delete-area', args=['testid'])
        assert url == '/areas/delete/testid'

    def test_get_block_async_by_area_url_pattern(self):
        """Test get-block-async-by-area URL pattern with ID"""
        url = reverse('get-block-async-by-area', args=[42])
        assert url == '/areas/get_block_async_by_area/42/'


class TestAreasUrlReverse(BaseAPITestNoDatabase):
    """Test URL reverse functionality"""

    def test_areas_url_reverse(self):
        """Test areas URL can be reversed by name"""
        url = reverse('areas')
        assert url is not None

    def test_filter_areas_url_reverse(self):
        """Test filter-areas URL can be reversed by name"""
        url = reverse('filter-areas')
        assert url is not None

    def test_new_area_url_reverse(self):
        """Test new-area URL can be reversed by name"""
        url = reverse('new-area')
        assert url is not None

    def test_edit_area_url_reverse_with_args(self):
        """Test edit-area URL can be reversed with args"""
        url = reverse('edit-area', args=['testid'])
        assert url is not None
        assert '/edit/testid' in url

    def test_delete_area_url_reverse_with_args(self):
        """Test delete-area URL can be reversed with args"""
        url = reverse('delete-area', args=['testid'])
        assert url is not None
        assert '/delete/testid' in url

    def test_get_block_async_by_area_url_reverse_with_args(self):
        """Test get-block-async-by-area URL can be reversed with args"""
        url = reverse('get-block-async-by-area', args=[1])
        assert url is not None
        assert '/get_block_async_by_area/1/' in url


class TestAreasUrlNames(BaseAPITestNoDatabase):
    """Test URL names are correctly defined"""

    def test_areas_url_name(self):
        """Test areas URL name"""
        url = reverse('areas')
        resolved = resolve(url)
        assert resolved.url_name == 'areas'

    def test_filter_areas_url_name(self):
        """Test filter-areas URL name"""
        url = reverse('filter-areas')
        resolved = resolve(url)
        assert resolved.url_name == 'filter-areas'

    def test_new_area_url_name(self):
        """Test new-area URL name"""
        url = reverse('new-area')
        resolved = resolve(url)
        assert resolved.url_name == 'new-area'

    def test_edit_area_url_name(self):
        """Test edit-area URL name"""
        url = reverse('edit-area', args=['testid'])
        resolved = resolve(url)
        assert resolved.url_name == 'edit-area'

    def test_delete_area_url_name(self):
        """Test delete-area URL name"""
        url = reverse('delete-area', args=['testid'])
        resolved = resolve(url)
        assert resolved.url_name == 'delete-area'

    def test_get_block_async_by_area_url_name(self):
        """Test get-block-async-by-area URL name"""
        url = reverse('get-block-async-by-area', args=[1])
        resolved = resolve(url)
        assert resolved.url_name == 'get-block-async-by-area'


class TestAreasUrlParameters(BaseAPITestNoDatabase):
    """Test URL parameters are correctly parsed"""

    def test_edit_area_url_extracts_id(self):
        """Test edit-area URL extracts id parameter"""
        url = '/areas/edit/test123'
        resolved = resolve(url)

        assert 'id' in resolved.kwargs
        assert resolved.kwargs['id'] == 'test123'

    def test_delete_area_url_extracts_id(self):
        """Test delete-area URL extracts id parameter"""
        url = '/areas/delete/test456'
        resolved = resolve(url)

        assert 'id' in resolved.kwargs
        assert resolved.kwargs['id'] == 'test456'

    def test_get_block_async_by_area_url_extracts_id(self):
        """Test get-block-async-by-area URL extracts id parameter"""
        url = '/areas/get_block_async_by_area/99/'
        resolved = resolve(url)

        assert 'id' in resolved.kwargs
        assert resolved.kwargs['id'] == 99

    def test_edit_area_url_with_different_ids(self):
        """Test edit-area URL works with different IDs"""
        for test_id in ['id1', 'id2', 'id3']:
            url = reverse('edit-area', args=[test_id])
            resolved = resolve(url)
            assert resolved.kwargs['id'] == test_id

    def test_delete_area_url_with_different_ids(self):
        """Test delete-area URL works with different IDs"""
        for test_id in ['del1', 'del2', 'del3']:
            url = reverse('delete-area', args=[test_id])
            resolved = resolve(url)
            assert resolved.kwargs['id'] == test_id

    def test_get_block_async_by_area_url_with_different_ids(self):
        """Test get-block-async-by-area URL works with different IDs"""
        for test_id in [1, 2, 3]:
            url = reverse('get-block-async-by-area', args=[test_id])
            resolved = resolve(url)
            assert resolved.kwargs['id'] == test_id
