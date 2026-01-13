# tests/unit/blocks/test_urls.py
"""
Blocks URLs Test Cases - No Database Required
"""
import pytest
from django.urls import reverse, resolve
from tests.utils.base_test import BaseAPITestNoDatabase


class TestBlocksUrls(BaseAPITestNoDatabase):
    """Test blocks URL patterns"""

    def test_blocks_url_resolves(self):
        """Test blocks URL resolves to correct view"""
        from blocks import views

        url = reverse('blocks')
        resolved = resolve(url)

        assert resolved.func == views.blocks

    def test_filter_blocks_url_resolves(self):
        """Test filter-blocks URL resolves to correct view"""
        from blocks import views

        url = reverse('filter-blocks')
        resolved = resolve(url)

        assert resolved.func == views.filter_blocks

    def test_new_block_url_resolves(self):
        """Test new-block URL resolves to correct view"""
        from blocks import views

        url = reverse('new-block')
        resolved = resolve(url)

        assert resolved.func == views.new_block

    def test_add_block_to_patient_async_url_resolves(self):
        """Test add-block-to-patient-async URL resolves to correct view"""
        from blocks import views

        url = reverse('add-block-to-patient-async')
        resolved = resolve(url)

        assert resolved.func == views.add_block_to_patient_async

    def test_add_block_to_project_async_url_resolves(self):
        """Test add-block-to-project-async URL resolves to correct view"""
        from blocks import views

        url = reverse('add-block-to-project-async')
        resolved = resolve(url)

        assert resolved.func == views.add_block_to_project_async

    def test_remove_block_from_project_async_url_resolves(self):
        """Test remove-block-from-project-async URL resolves to correct view"""
        from blocks import views

        url = reverse('remove-block-from-project-async')
        resolved = resolve(url)

        assert resolved.func == views.remove_block_from_project_async

    def test_remove_block_from_patient_async_url_resolves(self):
        """Test remove-block-from-patient-async URL resolves to correct view"""
        from blocks import views

        url = reverse('remove-block-from-patient-async')
        resolved = resolve(url)

        assert resolved.func == views.remove_block_from_patient_async

    def test_edit_block_url_resolves(self):
        """Test edit-block URL resolves to correct view"""
        from blocks import views

        url = reverse('edit-block', args=['test123'])
        resolved = resolve(url)

        assert resolved.func == views.edit_block

    def test_edit_block_async_url_resolves(self):
        """Test edit-block-async URL resolves to correct view"""
        from blocks import views

        url = reverse('edit-block-async')
        resolved = resolve(url)

        assert resolved.func == views.edit_block_async

    def test_delete_block_url_resolves(self):
        """Test delete-block URL resolves to correct view"""
        from blocks import views

        url = reverse('delete-block', args=['test123'])
        resolved = resolve(url)

        assert resolved.func == views.delete_block

    def test_delete_batch_blocks_url_resolves(self):
        """Test delete-batch-blocks URL resolves to correct view"""
        from blocks import views

        url = reverse('delete-batch-blocks')
        resolved = resolve(url)

        assert resolved.func == views.delete_batch_blocks


    def test_get_block_async_url_resolves(self):
        """Test get-get_block_async URL resolves to correct view"""
        from blocks import views

        url = reverse('get-get_block_async')
        resolved = resolve(url)

        assert resolved.func == views.get_block_async

    def test_export_csv_all_data_url_resolves(self):
        """Test export-csv-all-data URL resolves to correct view"""
        from blocks import views

        url = reverse('export-csv-all-data')
        resolved = resolve(url)

        assert resolved.func == views.export_csv_all_data

    def test_edit_block_url_view_resolves(self):
        """Test edit_block_url URL resolves to correct view"""
        from blocks import views

        url = reverse('edit_block_url')
        resolved = resolve(url)

        assert resolved.func == views.edit_block_url

    def test_get_block_areas_url_resolves(self):
        """Test get-block-areas URL resolves to correct view"""
        from blocks import views

        url = reverse('get-block-areas', args=[1])
        resolved = resolve(url)

        assert resolved.func == views.get_block_areas


class TestBlocksUrlPatterns(BaseAPITestNoDatabase):
    """Test URL patterns structure"""

    def test_blocks_url_pattern(self):
        """Test blocks URL pattern"""
        url = reverse('blocks')
        assert url == '/blocks/'

    def test_filter_blocks_url_pattern(self):
        """Test filter-blocks URL pattern"""
        url = reverse('filter-blocks')
        assert url == '/blocks/filter_blocks'

    def test_new_block_url_pattern(self):
        """Test new-block URL pattern"""
        url = reverse('new-block')
        assert url == '/blocks/new'

    def test_edit_block_url_pattern(self):
        """Test edit-block URL pattern with ID"""
        url = reverse('edit-block', args=['testid'])
        assert url == '/blocks/edit/testid'

    def test_delete_block_url_pattern(self):
        """Test delete-block URL pattern with ID"""
        url = reverse('delete-block', args=['testid'])
        assert url == '/blocks/delete/testid'

    def test_get_block_areas_url_pattern(self):
        """Test get-block-areas URL pattern with ID"""
        url = reverse('get-block-areas', args=[42])
        assert url == '/blocks/get_block_areas/42/'


class TestBlocksUrlReverse(BaseAPITestNoDatabase):
    """Test URL reverse functionality"""

    def test_blocks_url_reverse(self):
        """Test blocks URL can be reversed by name"""
        url = reverse('blocks')
        assert url is not None

    def test_filter_blocks_url_reverse(self):
        """Test filter-blocks URL can be reversed by name"""
        url = reverse('filter-blocks')
        assert url is not None

    def test_new_block_url_reverse(self):
        """Test new-block URL can be reversed by name"""
        url = reverse('new-block')
        assert url is not None

    def test_edit_block_url_reverse_with_args(self):
        """Test edit-block URL can be reversed with args"""
        url = reverse('edit-block', args=['testid'])
        assert url is not None
        assert '/edit/testid' in url

    def test_delete_block_url_reverse_with_args(self):
        """Test delete-block URL can be reversed with args"""
        url = reverse('delete-block', args=['testid'])
        assert url is not None
        assert '/delete/testid' in url

    def test_get_block_areas_url_reverse_with_args(self):
        """Test get-block-areas URL can be reversed with args"""
        url = reverse('get-block-areas', args=[1])
        assert url is not None
        assert '/get_block_areas/1/' in url


class TestBlocksUrlNames(BaseAPITestNoDatabase):
    """Test URL names are correctly defined"""

    def test_blocks_url_name(self):
        """Test blocks URL name"""
        url = reverse('blocks')
        resolved = resolve(url)
        assert resolved.url_name == 'blocks'

    def test_filter_blocks_url_name(self):
        """Test filter-blocks URL name"""
        url = reverse('filter-blocks')
        resolved = resolve(url)
        assert resolved.url_name == 'filter-blocks'

    def test_new_block_url_name(self):
        """Test new-block URL name"""
        url = reverse('new-block')
        resolved = resolve(url)
        assert resolved.url_name == 'new-block'

    def test_edit_block_url_name(self):
        """Test edit-block URL name"""
        url = reverse('edit-block', args=['testid'])
        resolved = resolve(url)
        assert resolved.url_name == 'edit-block'

    def test_delete_block_url_name(self):
        """Test delete-block URL name"""
        url = reverse('delete-block', args=['testid'])
        resolved = resolve(url)
        assert resolved.url_name == 'delete-block'

    def test_get_block_areas_url_name(self):
        """Test get-block-areas URL name"""
        url = reverse('get-block-areas', args=[1])
        resolved = resolve(url)
        assert resolved.url_name == 'get-block-areas'


class TestBlocksUrlParameters(BaseAPITestNoDatabase):
    """Test URL parameters are correctly parsed"""

    def test_edit_block_url_extracts_id(self):
        """Test edit-block URL extracts id parameter"""
        url = '/blocks/edit/test123'
        resolved = resolve(url)

        assert 'id' in resolved.kwargs
        assert resolved.kwargs['id'] == 'test123'

    def test_delete_block_url_extracts_id(self):
        """Test delete-block URL extracts id parameter"""
        url = '/blocks/delete/test456'
        resolved = resolve(url)

        assert 'id' in resolved.kwargs
        assert resolved.kwargs['id'] == 'test456'

    def test_get_block_areas_url_extracts_id(self):
        """Test get-block-areas URL extracts id parameter"""
        url = '/blocks/get_block_areas/99/'
        resolved = resolve(url)

        assert 'id' in resolved.kwargs
        assert resolved.kwargs['id'] == 99

    def test_edit_block_url_with_different_ids(self):
        """Test edit-block URL works with different IDs"""
        for test_id in ['id1', 'id2', 'id3']:
            url = reverse('edit-block', args=[test_id])
            resolved = resolve(url)
            assert resolved.kwargs['id'] == test_id

    def test_delete_block_url_with_different_ids(self):
        """Test delete-block URL works with different IDs"""
        for test_id in ['del1', 'del2', 'del3']:
            url = reverse('delete-block', args=[test_id])
            resolved = resolve(url)
            assert resolved.kwargs['id'] == test_id

    def test_get_block_areas_url_with_different_ids(self):
        """Test get-block-areas URL works with different IDs"""
        for test_id in [1, 2, 3]:
            url = reverse('get-block-areas', args=[test_id])
            resolved = resolve(url)
            assert resolved.kwargs['id'] == test_id
