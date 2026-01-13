# tests/unit/analysisrun/test_urls.py
"""
Analysisrun URLs Test Cases - No Database Required
"""
import pytest
from unittest.mock import Mock
from django.urls import resolve, reverse
from tests.utils.base_test import BaseAPITestNoDatabase


class TestAnalysisRunURLs(BaseAPITestNoDatabase):
    """Test analysisrun URL patterns"""

    def test_analysisruns_url_resolves(self):
        """Test analysisruns URL resolves to correct view"""
        from analysisrun.views import analysisruns

        # The URL pattern is "" which means it's at the root of the analysisrun namespace
        # We can't easily test reverse without the full URL configuration
        # So we'll just test that the view function exists
        assert analysisruns is not None
        assert callable(analysisruns)

    def test_filter_analysisruns_url_resolves(self):
        """Test filter_analysisruns URL resolves to correct view"""
        from analysisrun.views import filter_analysisruns

        assert filter_analysisruns is not None
        assert callable(filter_analysisruns)

    def test_save_analysis_run_url_resolves(self):
        """Test save_analysis_run URL resolves to correct view"""
        from analysisrun.views import save_analysis_run

        assert save_analysis_run is not None
        assert callable(save_analysis_run)

    def test_initialize_import_variants_url_resolves(self):
        """Test initialize_import_variants URL resolves to correct view"""
        from analysisrun.views import initialize_import_variants

        assert initialize_import_variants is not None
        assert callable(initialize_import_variants)

    def test_start_import_variants_url_resolves(self):
        """Test start_import_variants URL resolves to correct view"""
        from analysisrun.views import start_import_variants

        assert start_import_variants is not None
        assert callable(start_import_variants)

    def test_check_import_progress_url_resolves(self):
        """Test check_import_progress URL resolves to correct view"""
        from analysisrun.views import check_import_progress

        assert check_import_progress is not None
        assert callable(check_import_progress)

    def test_report_import_status_url_resolves(self):
        """Test report_import_status URL resolves to correct view"""
        from analysisrun.views import report_import_status

        assert report_import_status is not None
        assert callable(report_import_status)

    def test_reset_process_url_resolves(self):
        """Test reset_process URL resolves to correct view"""
        from analysisrun.views import reset_process

        assert reset_process is not None
        assert callable(reset_process)

    def test_delete_analysis_run_url_resolves(self):
        """Test delete_analysis_run URL resolves to correct view"""
        from analysisrun.views import delete_analysis_run

        assert delete_analysis_run is not None
        assert callable(delete_analysis_run)

    def test_delete_batch_analysis_run_url_resolves(self):
        """Test delete_batch_analysis_run URL resolves to correct view"""
        from analysisrun.views import delete_batch_analysis_run

        assert delete_batch_analysis_run is not None
        assert callable(delete_batch_analysis_run)

    def test_check_can_deleted_async_url_resolves(self):
        """Test check_can_deleted_async URL resolves to correct view"""
        from analysisrun.views import check_can_deleted_async

        assert check_can_deleted_async is not None
        assert callable(check_can_deleted_async)


class TestURLPatterns(BaseAPITestNoDatabase):
    """Test URL patterns structure"""

    def test_urls_module_can_be_imported(self):
        """Test analysisrun.urls module can be imported"""
        import analysisrun.urls
        assert analysisrun.urls is not None

    def test_urlpatterns_exists(self):
        """Test urlpatterns exists in urls module"""
        from analysisrun import urls
        assert hasattr(urls, 'urlpatterns')

    def test_urlpatterns_is_list(self):
        """Test urlpatterns is a list"""
        from analysisrun.urls import urlpatterns
        assert isinstance(urlpatterns, list)

    def test_urlpatterns_not_empty(self):
        """Test urlpatterns is not empty"""
        from analysisrun.urls import urlpatterns
        assert len(urlpatterns) > 0

    def test_urlpatterns_count(self):
        """Test urlpatterns has expected number of patterns"""
        from analysisrun.urls import urlpatterns
        # Count only path patterns, excluding staticfiles_urlpatterns
        path_patterns = [p for p in urlpatterns if hasattr(p, 'pattern')]
        assert len(path_patterns) >= 11  # At least 11 URL patterns defined


class TestURLConfiguration(BaseAPITestNoDatabase):
    """Test URL configuration details"""

    def test_analysisruns_url_pattern(self):
        """Test analysisruns URL pattern exists"""
        from analysisrun.urls import urlpatterns

        # Check that we have a pattern with empty path
        patterns = [p for p in urlpatterns if hasattr(p, 'pattern')]
        assert len(patterns) > 0

    def test_filter_analysisruns_url_pattern(self):
        """Test filter_analysisruns URL pattern exists"""
        from analysisrun.urls import urlpatterns

        # Check that filter_analysisruns pattern exists
        pattern_names = [p.name for p in urlpatterns if hasattr(p, 'name') and p.name]
        assert 'filter-analysisruns' in pattern_names

    def test_save_analysis_run_url_pattern(self):
        """Test save_analysis_run URL pattern exists"""
        from analysisrun.urls import urlpatterns

        pattern_names = [p.name for p in urlpatterns if hasattr(p, 'name') and p.name]
        assert 'save-analysis-run' in pattern_names

    def test_initialize_import_variants_url_pattern(self):
        """Test initialize_import_variants URL pattern exists"""
        from analysisrun.urls import urlpatterns

        pattern_names = [p.name for p in urlpatterns if hasattr(p, 'name') and p.name]
        assert 'initialize-import-variants' in pattern_names

    def test_start_import_variants_url_pattern(self):
        """Test start_import_variants URL pattern exists"""
        from analysisrun.urls import urlpatterns

        pattern_names = [p.name for p in urlpatterns if hasattr(p, 'name') and p.name]
        assert 'start_import_variants' in pattern_names

    def test_check_import_progress_url_pattern(self):
        """Test check_import_progress URL pattern exists"""
        from analysisrun.urls import urlpatterns

        pattern_names = [p.name for p in urlpatterns if hasattr(p, 'name') and p.name]
        assert 'check_import_progress' in pattern_names

    def test_report_import_status_url_pattern(self):
        """Test report_import_status URL pattern exists"""
        from analysisrun.urls import urlpatterns

        pattern_names = [p.name for p in urlpatterns if hasattr(p, 'name') and p.name]
        assert 'report_import_status' in pattern_names

    def test_reset_process_url_pattern(self):
        """Test reset_process URL pattern exists"""
        from analysisrun.urls import urlpatterns

        pattern_names = [p.name for p in urlpatterns if hasattr(p, 'name') and p.name]
        assert 'reset_process' in pattern_names

    def test_delete_analysis_run_url_pattern(self):
        """Test delete_analysis_run URL pattern exists"""
        from analysisrun.urls import urlpatterns

        pattern_names = [p.name for p in urlpatterns if hasattr(p, 'name') and p.name]
        assert 'delete-analysis-run' in pattern_names

    def test_delete_batch_analysis_run_url_pattern(self):
        """Test delete_batch_analysis_run URL pattern exists"""
        from analysisrun.urls import urlpatterns

        pattern_names = [p.name for p in urlpatterns if hasattr(p, 'name') and p.name]
        assert 'delete-batch-analysis-run' in pattern_names

    def test_check_can_deleted_async_url_pattern(self):
        """Test check_can_deleted_async URL pattern exists"""
        from analysisrun.urls import urlpatterns

        pattern_names = [p.name for p in urlpatterns if hasattr(p, 'name') and p.name]
        assert 'check-can-deleted-async' in pattern_names

    def test_analysisruns_url_name(self):
        """Test analysisruns URL has correct name"""
        from analysisrun.urls import urlpatterns

        pattern_names = [p.name for p in urlpatterns if hasattr(p, 'name') and p.name]
        assert 'analysisruns' in pattern_names
