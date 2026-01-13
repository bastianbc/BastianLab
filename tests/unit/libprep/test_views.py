# tests/unit/libprep/test_views.py
"""
Libprep Views Test Cases - No Database Required
"""
import json
from unittest.mock import Mock, patch, MagicMock
from django.http import JsonResponse
from tests.utils.base_test import BaseAPITestNoDatabase
from tests.fixtures.libprep_fixtures import LibprepTestData


class TestViewsImport(BaseAPITestNoDatabase):
    """Test views can be imported"""

    def test_nucacids_view_exists(self):
        """Test nucacids view can be imported"""
        from libprep.views import nucacids
        assert nucacids is not None

    def test_filter_nucacids_view_exists(self):
        """Test filter_nucacids view can be imported"""
        from libprep.views import filter_nucacids
        assert filter_nucacids is not None

    def test_edit_nucacid_async_view_exists(self):
        """Test edit_nucacid_async view can be imported"""
        from libprep.views import edit_nucacid_async
        assert edit_nucacid_async is not None

    def test_new_nucacid_view_exists(self):
        """Test new_nucacid view can be imported"""
        from libprep.views import new_nucacid
        assert new_nucacid is not None

    def test_new_nucacid_async_view_exists(self):
        """Test new_nucacid_async view can be imported"""
        from libprep.views import new_nucacid_async
        assert new_nucacid_async is not None

    def test_edit_nucacid_view_exists(self):
        """Test edit_nucacid view can be imported"""
        from libprep.views import edit_nucacid
        assert edit_nucacid is not None

    def test_delete_nucacid_view_exists(self):
        """Test delete_nucacid view can be imported"""
        from libprep.views import delete_nucacid
        assert delete_nucacid is not None

    def test_delete_batch_nucacids_view_exists(self):
        """Test delete_batch_nucacids view can be imported"""
        from libprep.views import delete_batch_nucacids
        assert delete_batch_nucacids is not None

    def test_get_na_types_view_exists(self):
        """Test get_na_types view can be imported"""
        from libprep.views import get_na_types
        assert get_na_types is not None

    def test_check_can_deleted_async_view_exists(self):
        """Test check_can_deleted_async view can be imported"""
        from libprep.views import check_can_deleted_async
        assert check_can_deleted_async is not None


class TestViewsDecorators(BaseAPITestNoDatabase):
    """Test views have correct decorators"""

    def test_nucacids_has_permission_decorator(self):
        """Test nucacids has permission_required decorator"""
        from libprep.views import nucacids

        assert hasattr(nucacids, '__wrapped__')

    def test_filter_nucacids_has_permission_decorator(self):
        """Test filter_nucacids has permission_required_for_async decorator"""
        from libprep.views import filter_nucacids

        assert hasattr(filter_nucacids, '__wrapped__')

    def test_edit_nucacid_async_has_permission_decorator(self):
        """Test edit_nucacid_async has permission_required_for_async decorator"""
        from libprep.views import edit_nucacid_async

        assert hasattr(edit_nucacid_async, '__wrapped__')

    def test_new_nucacid_has_permission_decorator(self):
        """Test new_nucacid has permission_required decorator"""
        from libprep.views import new_nucacid

        assert hasattr(new_nucacid, '__wrapped__')

    def test_new_nucacid_async_has_permission_decorator(self):
        """Test new_nucacid_async has permission_required_for_async decorator"""
        from libprep.views import new_nucacid_async

        assert hasattr(new_nucacid_async, '__wrapped__')

    def test_edit_nucacid_has_permission_decorator(self):
        """Test edit_nucacid has permission_required decorator"""
        from libprep.views import edit_nucacid

        assert hasattr(edit_nucacid, '__wrapped__')

    def test_delete_nucacid_has_permission_decorator(self):
        """Test delete_nucacid has permission_required decorator"""
        from libprep.views import delete_nucacid

        assert hasattr(delete_nucacid, '__wrapped__')

    def test_delete_batch_nucacids_has_permission_decorator(self):
        """Test delete_batch_nucacids has permission_required decorator"""
        from libprep.views import delete_batch_nucacids

        assert hasattr(delete_batch_nucacids, '__wrapped__')


class TestGetNaTypesView(BaseAPITestNoDatabase):
    """Test get_na_types view - no permission decorator"""

    def test_get_na_types_returns_json(self):
        """Test get_na_types returns JsonResponse"""
        from libprep.views import get_na_types

        request = self.create_request(
            method='GET',
            path='/libprep/get_na_types',
            user=self.user
        )

        response = get_na_types(request)

        assert isinstance(response, JsonResponse)

    def test_get_na_types_returns_formatted_data(self):
        """Test get_na_types returns correctly formatted data"""
        from libprep.views import get_na_types
        import json

        request = self.create_request(
            method='GET',
            path='/libprep/get_na_types',
            user=self.user
        )

        response = get_na_types(request)

        # Parse response content
        content = json.loads(response.content)

        # Should be a list
        assert isinstance(content, list)
        # Should have 3 items (1 empty + 2 NA types, BOTH is excluded)
        assert len(content) == 3
        # First item should be empty option
        assert content[0]['label'] == '---------'
        assert content[0]['value'] == ''

    def test_get_na_types_includes_dna_and_rna(self):
        """Test get_na_types includes DNA and RNA but not BOTH"""
        from libprep.views import get_na_types
        import json

        request = self.create_request(
            method='GET',
            path='/libprep/get_na_types',
            user=self.user
        )

        response = get_na_types(request)

        # Parse response content
        content = json.loads(response.content)

        # Extract values (excluding empty option)
        values = [item['value'] for item in content[1:]]
        labels = [item['label'] for item in content[1:]]

        assert 'dna' in values
        assert 'rna' in values
        assert 'both' not in values
        assert 'DNA' in labels
        assert 'RNA' in labels


class TestHelperFunctions(BaseAPITestNoDatabase):
    """Test helper functions"""

    def test_generate_unique_name_function_exists(self):
        """Test _generate_unique_name function exists"""
        from libprep.views import _generate_unique_name

        assert _generate_unique_name is not None
        assert callable(_generate_unique_name)
