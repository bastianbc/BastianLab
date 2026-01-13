# tests/unit/areas/test_views.py
"""
Areas Views Test Cases - No Database Required
"""
import json
from unittest.mock import Mock, patch, MagicMock
from django.http import JsonResponse
from tests.utils.base_test import BaseAPITestNoDatabase
from tests.fixtures.areas_fixtures import AreasTestData


class TestViewsImport(BaseAPITestNoDatabase):
    """Test views can be imported"""

    def test_filter_areas_view_exists(self):
        """Test filter_areas view can be imported"""
        from areas.views import filter_areas
        assert filter_areas is not None

    def test_areas_view_exists(self):
        """Test areas view can be imported"""
        from areas.views import areas
        assert areas is not None

    def test_new_area_view_exists(self):
        """Test new_area view can be imported"""
        from areas.views import new_area
        assert new_area is not None

    def test_add_area_to_block_async_view_exists(self):
        """Test add_area_to_block_async view can be imported"""
        from areas.views import add_area_to_block_async
        assert add_area_to_block_async is not None

    def test_edit_area_view_exists(self):
        """Test edit_area view can be imported"""
        from areas.views import edit_area
        assert edit_area is not None

    def test_edit_area_async_view_exists(self):
        """Test edit_area_async view can be imported"""
        from areas.views import edit_area_async
        assert edit_area_async is not None

    def test_delete_area_view_exists(self):
        """Test delete_area view can be imported"""
        from areas.views import delete_area
        assert delete_area is not None

    def test_delete_batch_areas_view_exists(self):
        """Test delete_batch_areas view can be imported"""
        from areas.views import delete_batch_areas
        assert delete_batch_areas is not None

    def test_check_can_deleted_async_view_exists(self):
        """Test check_can_deleted_async view can be imported"""
        from areas.views import check_can_deleted_async
        assert check_can_deleted_async is not None

    def test_get_collections_view_exists(self):
        """Test get_collections view can be imported"""
        from areas.views import get_collections
        assert get_collections is not None

    def test_get_area_types_view_exists(self):
        """Test get_area_types view can be imported"""
        from areas.views import get_area_types
        assert get_area_types is not None

    def test_get_block_async_by_area_view_exists(self):
        """Test get_block_async_by_area view can be imported"""
        from areas.views import get_block_async_by_area
        assert get_block_async_by_area is not None


class TestViewsDecorators(BaseAPITestNoDatabase):
    """Test views have correct decorators"""

    def test_filter_areas_has_permission_decorator(self):
        """Test filter_areas has permission_required_for_async decorator"""
        from areas.views import filter_areas

        assert hasattr(filter_areas, '__wrapped__')

    def test_areas_has_permission_decorator(self):
        """Test areas has permission_required decorator"""
        from areas.views import areas

        assert hasattr(areas, '__wrapped__')

    def test_new_area_has_permission_decorator(self):
        """Test new_area has permission_required decorator"""
        from areas.views import new_area

        assert hasattr(new_area, '__wrapped__')

    def test_edit_area_has_permission_decorator(self):
        """Test edit_area has permission_required decorator"""
        from areas.views import edit_area

        assert hasattr(edit_area, '__wrapped__')

    def test_delete_batch_areas_has_permission_decorator(self):
        """Test delete_batch_areas has permission_required decorator"""
        from areas.views import delete_batch_areas

        assert hasattr(delete_batch_areas, '__wrapped__')


class TestGetCollectionsView(BaseAPITestNoDatabase):
    """Test get_collections view - no permission decorator"""

    @patch('areas.views.Block')
    def test_get_collections_returns_json(self, mock_block_class):
        """Test get_collections returns JsonResponse"""
        from areas.views import get_collections

        # Mock Block.get_collections
        mock_block_class.get_collections.return_value = [
            {'label': '---------', 'value': ''},
            {'label': 'Punch', 'value': 'PU'}
        ]

        request = self.create_request(
            method='GET',
            path='/areas/get_collections',
            user=self.user
        )

        response = get_collections(request)

        assert isinstance(response, JsonResponse)
        mock_block_class.get_collections.assert_called_once()


class TestGetAreaTypesView(BaseAPITestNoDatabase):
    """Test get_area_types view - no permission decorator"""

    @patch('areas.views.AreaType.objects')
    def test_get_area_types_returns_json(self, mock_areatype_objects):
        """Test get_area_types returns JsonResponse"""
        from areas.views import get_area_types

        # Mock area types
        mock_areatype_objects.all.return_value.values.return_value.order_by.return_value = [
            {'id': 1, 'name': 'Type A'},
            {'id': 2, 'name': 'Type B'}
        ]

        request = self.create_request(
            method='GET',
            path='/areas/get_area_types',
            user=self.user
        )

        response = get_area_types(request)

        assert isinstance(response, JsonResponse)

    @patch('areas.views.AreaType.objects')
    def test_get_area_types_returns_formatted_data(self, mock_areatype_objects):
        """Test get_area_types returns correctly formatted data"""
        from areas.views import get_area_types
        import json

        # Mock area types
        mock_areatype_objects.all.return_value.values.return_value.order_by.return_value = [
            {'id': 1, 'name': 'Type A'},
            {'id': 2, 'name': 'Type B'}
        ]

        request = self.create_request(
            method='GET',
            path='/areas/get_area_types',
            user=self.user
        )

        response = get_area_types(request)

        # Parse response content
        content = json.loads(response.content)

        # Should be a list
        assert isinstance(content, list)
        # Should have 2 items
        assert len(content) == 2
        # Each item should have 'value' and 'name' keys
        assert 'value' in content[0]
        assert 'name' in content[0]


class TestGetBlockAsyncByAreaView(BaseAPITestNoDatabase):
    """Test get_block_async_by_area view - no permission decorator"""

    @patch('areas.views.Area.objects')
    def test_get_block_async_by_area_returns_json(self, mock_area_objects):
        """Test get_block_async_by_area returns JsonResponse"""
        from areas.views import get_block_async_by_area

        # Mock patient
        mock_patient = Mock()
        mock_patient.pat_id = 'PAT001'

        # Mock block
        mock_block = Mock()
        mock_block.id = 1
        mock_block.name = 'BLK001'
        mock_block.diagnosis = 'Melanoma'
        mock_block.scan_number = 'SCAN123'
        mock_block.patient = mock_patient
        mock_block.get_block_url.return_value = 'http://example.com/'

        # Mock area
        mock_area = Mock()
        mock_area.id = 1
        mock_area.block = mock_block

        mock_area_objects.get.return_value = mock_area

        request = self.create_request(
            method='GET',
            path='/areas/get_block_async_by_area/1/',
            user=self.user
        )

        response = get_block_async_by_area(request, id=1)

        assert isinstance(response, JsonResponse)
        mock_area_objects.get.assert_called_once_with(id=1)

    @patch('areas.views.Area.objects')
    def test_get_block_async_by_area_returns_correct_structure(self, mock_area_objects):
        """Test get_block_async_by_area returns correct JSON structure"""
        from areas.views import get_block_async_by_area
        import json

        # Mock patient
        mock_patient = Mock()
        mock_patient.pat_id = 'PAT001'

        # Mock block
        mock_block = Mock()
        mock_block.id = 1
        mock_block.name = 'BLK001'
        mock_block.diagnosis = 'Melanoma'
        mock_block.scan_number = 'SCAN123'
        mock_block.patient = mock_patient
        mock_block.get_block_url.return_value = 'http://example.com/'

        # Mock area
        mock_area = Mock()
        mock_area.id = 1
        mock_area.block = mock_block

        mock_area_objects.get.return_value = mock_area

        request = self.create_request(
            method='GET',
            path='/areas/get_block_async_by_area/1/',
            user=self.user
        )

        response = get_block_async_by_area(request, id=1)

        # Parse response content
        content = json.loads(response.content)

        assert 'block' in content
        assert 'patient_id' in content
        assert content['patient_id'] == 'PAT001'
        assert content['block']['id'] == 1
        assert content['block']['name'] == 'BLK001'


