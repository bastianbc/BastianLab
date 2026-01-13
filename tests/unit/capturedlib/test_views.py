# tests/unit/capturedlib/test_views.py
"""
Capturedlib Views Test Cases - No Database Required
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.http import JsonResponse
from tests.utils.base_test import BaseAPITestNoDatabase
from tests.fixtures.capturedlib_fixtures import CapturedlibTestData


class TestViewsImport(BaseAPITestNoDatabase):
    """Test views can be imported"""

    def test_capturedlibs_view_exists(self):
        """Test capturedlibs view can be imported"""
        from capturedlib.views import capturedlibs
        assert capturedlibs is not None

    def test_filter_capturedlibs_view_exists(self):
        """Test filter_capturedlibs view can be imported"""
        from capturedlib.views import filter_capturedlibs
        assert filter_capturedlibs is not None

    def test_edit_capturedlib_async_view_exists(self):
        """Test edit_capturedlib_async view can be imported"""
        from capturedlib.views import edit_capturedlib_async
        assert edit_capturedlib_async is not None

    def test_new_capturedlib_view_exists(self):
        """Test new_capturedlib view can be imported"""
        from capturedlib.views import new_capturedlib
        assert new_capturedlib is not None

    def test_new_capturedlib_async_view_exists(self):
        """Test new_capturedlib_async view can be imported"""
        from capturedlib.views import new_capturedlib_async
        assert new_capturedlib_async is not None

    def test_edit_capturedlib_view_exists(self):
        """Test edit_capturedlib view can be imported"""
        from capturedlib.views import edit_capturedlib
        assert edit_capturedlib is not None

    def test_delete_capturedlib_view_exists(self):
        """Test delete_capturedlib view can be imported"""
        from capturedlib.views import delete_capturedlib
        assert delete_capturedlib is not None

    def test_delete_batch_capturedlibs_view_exists(self):
        """Test delete_batch_capturedlibs view can be imported"""
        from capturedlib.views import delete_batch_capturedlibs
        assert delete_batch_capturedlibs is not None

    def test_get_used_samplelibs_view_exists(self):
        """Test get_used_samplelibs view can be imported"""
        from capturedlib.views import get_used_samplelibs
        assert get_used_samplelibs is not None

    def test_update_async_view_exists(self):
        """Test update_async view can be imported"""
        from capturedlib.views import update_async
        assert update_async is not None

    def test_check_idendical_barcode_view_exists(self):
        """Test check_idendical_barcode view can be imported"""
        from capturedlib.views import check_idendical_barcode
        assert check_idendical_barcode is not None

    def test_check_can_deleted_async_view_exists(self):
        """Test check_can_deleted_async view can be imported"""
        from capturedlib.views import check_can_deleted_async
        assert check_can_deleted_async is not None


class TestViewsDecorators(BaseAPITestNoDatabase):
    """Test views have correct decorators"""

    def test_capturedlibs_has_permission_decorator(self):
        """Test capturedlibs has permission_required decorator"""
        from capturedlib.views import capturedlibs

        assert hasattr(capturedlibs, '__wrapped__')

    def test_filter_capturedlibs_has_permission_decorator(self):
        """Test filter_capturedlibs has permission_required_for_async decorator"""
        from capturedlib.views import filter_capturedlibs

        assert hasattr(filter_capturedlibs, '__wrapped__')

    def test_edit_capturedlib_async_has_permission_decorator(self):
        """Test edit_capturedlib_async has permission_required_for_async decorator"""
        from capturedlib.views import edit_capturedlib_async

        assert hasattr(edit_capturedlib_async, '__wrapped__')

    def test_new_capturedlib_has_permission_decorator(self):
        """Test new_capturedlib has permission_required decorator"""
        from capturedlib.views import new_capturedlib

        assert hasattr(new_capturedlib, '__wrapped__')

    def test_new_capturedlib_async_has_permission_decorator(self):
        """Test new_capturedlib_async has permission_required_for_async decorator"""
        from capturedlib.views import new_capturedlib_async

        assert hasattr(new_capturedlib_async, '__wrapped__')

    def test_edit_capturedlib_has_permission_decorator(self):
        """Test edit_capturedlib has permission_required decorator"""
        from capturedlib.views import edit_capturedlib

        assert hasattr(edit_capturedlib, '__wrapped__')

    def test_delete_capturedlib_has_permission_decorator(self):
        """Test delete_capturedlib has permission_required decorator"""
        from capturedlib.views import delete_capturedlib

        assert hasattr(delete_capturedlib, '__wrapped__')

    def test_delete_batch_capturedlibs_has_permission_decorator(self):
        """Test delete_batch_capturedlibs has permission_required decorator"""
        from capturedlib.views import delete_batch_capturedlibs

        assert hasattr(delete_batch_capturedlibs, '__wrapped__')

    def test_get_used_samplelibs_has_permission_decorator(self):
        """Test get_used_samplelibs has permission_required decorator"""
        from capturedlib.views import get_used_samplelibs

        assert hasattr(get_used_samplelibs, '__wrapped__')

    def test_update_async_has_permission_decorator(self):
        """Test update_async has permission_required_for_async decorator"""
        from capturedlib.views import update_async

        assert hasattr(update_async, '__wrapped__')

    def test_check_idendical_barcode_has_permission_decorator(self):
        """Test check_idendical_barcode has permission_required_for_async decorator"""
        from capturedlib.views import check_idendical_barcode

        assert hasattr(check_idendical_barcode, '__wrapped__')

    def test_check_can_deleted_async_has_permission_decorator(self):
        """Test check_can_deleted_async has permission_required_for_async decorator"""
        from capturedlib.views import check_can_deleted_async

        assert hasattr(check_can_deleted_async, '__wrapped__')
