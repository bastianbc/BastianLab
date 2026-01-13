# tests/unit/sequencingrun/test_views.py
"""
Sequencingrun Views Test Cases - No Database Required
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.http import JsonResponse
from tests.utils.base_test import BaseAPITestNoDatabase
from tests.fixtures.sequencingrun_fixtures import SequencingrunTestData


class TestViewsImport(BaseAPITestNoDatabase):
    """Test views can be imported"""

    def test_sequencingruns_view_exists(self):
        """Test sequencingruns view can be imported"""
        from sequencingrun.views import sequencingruns
        assert sequencingruns is not None

    def test_filter_sequencingruns_view_exists(self):
        """Test filter_sequencingruns view can be imported"""
        from sequencingrun.views import filter_sequencingruns
        assert filter_sequencingruns is not None

    def test_edit_sequencingrun_async_view_exists(self):
        """Test edit_sequencingrun_async view can be imported"""
        from sequencingrun.views import edit_sequencingrun_async
        assert edit_sequencingrun_async is not None

    def test_new_sequencingrun_view_exists(self):
        """Test new_sequencingrun view can be imported"""
        from sequencingrun.views import new_sequencingrun
        assert new_sequencingrun is not None

    def test_new_sequencingrun_async_view_exists(self):
        """Test new_sequencingrun_async view can be imported"""
        from sequencingrun.views import new_sequencingrun_async
        assert new_sequencingrun_async is not None

    def test_edit_sequencingrun_view_exists(self):
        """Test edit_sequencingrun view can be imported"""
        from sequencingrun.views import edit_sequencingrun
        assert edit_sequencingrun is not None

    def test_delete_sequencingrun_view_exists(self):
        """Test delete_sequencingrun view can be imported"""
        from sequencingrun.views import delete_sequencingrun
        assert delete_sequencingrun is not None

    def test_delete_batch_sequencingruns_view_exists(self):
        """Test delete_batch_sequencingruns view can be imported"""
        from sequencingrun.views import delete_batch_sequencingruns
        assert delete_batch_sequencingruns is not None

    def test_get_used_sequencinglibs_view_exists(self):
        """Test get_used_sequencinglibs view can be imported"""
        from sequencingrun.views import get_used_sequencinglibs
        assert get_used_sequencinglibs is not None

    def test_check_can_deleted_async_view_exists(self):
        """Test check_can_deleted_async view can be imported"""
        from sequencingrun.views import check_can_deleted_async
        assert check_can_deleted_async is not None

    def test_get_facilities_view_exists(self):
        """Test get_facilities view can be imported"""
        from sequencingrun.views import get_facilities
        assert get_facilities is not None

    def test_get_sequencers_view_exists(self):
        """Test get_sequencers view can be imported"""
        from sequencingrun.views import get_sequencers
        assert get_sequencers is not None

    def test_get_pes_view_exists(self):
        """Test get_pes view can be imported"""
        from sequencingrun.views import get_pes
        assert get_pes is not None

    def test_add_async_view_exists(self):
        """Test add_async view can be imported"""
        from sequencingrun.views import add_async
        assert add_async is not None

    def test_get_sequencing_files_view_exists(self):
        """Test get_sequencing_files view can be imported"""
        from sequencingrun.views import get_sequencing_files
        assert get_sequencing_files is not None

    def test_save_sequencing_files_view_exists(self):
        """Test save_sequencing_files view can be imported"""
        from sequencingrun.views import save_sequencing_files
        assert save_sequencing_files is not None

    def test_get_sample_libs_async_view_exists(self):
        """Test get_sample_libs_async view can be imported"""
        from sequencingrun.views import get_sample_libs_async
        assert get_sample_libs_async is not None


class TestViewsDecorators(BaseAPITestNoDatabase):
    """Test views have correct decorators"""

    def test_sequencingruns_has_permission_decorator(self):
        """Test sequencingruns has permission_required decorator"""
        from sequencingrun.views import sequencingruns

        assert hasattr(sequencingruns, '__wrapped__')

    def test_filter_sequencingruns_has_permission_decorator(self):
        """Test filter_sequencingruns has permission_required_for_async decorator"""
        from sequencingrun.views import filter_sequencingruns

        assert hasattr(filter_sequencingruns, '__wrapped__')

    def test_edit_sequencingrun_async_has_permission_decorator(self):
        """Test edit_sequencingrun_async has permission_required_for_async decorator"""
        from sequencingrun.views import edit_sequencingrun_async

        assert hasattr(edit_sequencingrun_async, '__wrapped__')

    def test_new_sequencingrun_has_permission_decorator(self):
        """Test new_sequencingrun has permission_required decorator"""
        from sequencingrun.views import new_sequencingrun

        assert hasattr(new_sequencingrun, '__wrapped__')

    def test_new_sequencingrun_async_has_permission_decorator(self):
        """Test new_sequencingrun_async has permission_required_for_async decorator"""
        from sequencingrun.views import new_sequencingrun_async

        assert hasattr(new_sequencingrun_async, '__wrapped__')

    def test_edit_sequencingrun_has_permission_decorator(self):
        """Test edit_sequencingrun has permission_required decorator"""
        from sequencingrun.views import edit_sequencingrun

        assert hasattr(edit_sequencingrun, '__wrapped__')

    def test_delete_sequencingrun_has_permission_decorator(self):
        """Test delete_sequencingrun has permission_required decorator"""
        from sequencingrun.views import delete_sequencingrun

        assert hasattr(delete_sequencingrun, '__wrapped__')

    def test_delete_batch_sequencingruns_has_permission_decorator(self):
        """Test delete_batch_sequencingruns has permission_required decorator"""
        from sequencingrun.views import delete_batch_sequencingruns

        assert hasattr(delete_batch_sequencingruns, '__wrapped__')

    def test_get_used_sequencinglibs_has_permission_decorator(self):
        """Test get_used_sequencinglibs has permission_required decorator"""
        from sequencingrun.views import get_used_sequencinglibs

        assert hasattr(get_used_sequencinglibs, '__wrapped__')

    def test_check_can_deleted_async_has_permission_decorator(self):
        """Test check_can_deleted_async has permission_required_for_async decorator"""
        from sequencingrun.views import check_can_deleted_async

        assert hasattr(check_can_deleted_async, '__wrapped__')
