# tests/unit/analysisrun/test_forms.py
"""
Analysisrun Forms Test Cases - No Database Required
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django import forms
from tests.utils.base_test import BaseAPITestNoDatabase
from tests.fixtures.analysisrun_fixtures import AnalysisrunTestData


class TestAnalysisRunForm(BaseAPITestNoDatabase):
    """Test AnalysisRunForm"""

    def test_form_initialization(self):
        """Test AnalysisRunForm initializes correctly"""
        from analysisrun.forms import AnalysisRunForm

        form = AnalysisRunForm()
        assert form is not None

    def test_form_inherits_from_base_form(self):
        """Test AnalysisRunForm inherits from BaseForm"""
        from analysisrun.forms import AnalysisRunForm
        from core.forms import BaseForm

        assert issubclass(AnalysisRunForm, BaseForm)

    def test_form_meta_model(self):
        """Test form Meta.model is AnalysisRun"""
        from analysisrun.forms import AnalysisRunForm
        from analysisrun.models import AnalysisRun

        assert AnalysisRunForm.Meta.model == AnalysisRun

    def test_form_meta_fields(self):
        """Test form Meta.fields contains pipeline and genome"""
        from analysisrun.forms import AnalysisRunForm

        assert AnalysisRunForm.Meta.fields == ("pipeline", "genome")

    def test_form_has_pipeline_field(self):
        """Test form has pipeline field"""
        from analysisrun.forms import AnalysisRunForm

        form = AnalysisRunForm()
        assert 'pipeline' in form.fields

    def test_pipeline_field_is_required(self):
        """Test pipeline field is required"""
        from analysisrun.forms import AnalysisRunForm

        form = AnalysisRunForm()
        assert form.fields['pipeline'].required is True

    def test_form_has_genome_field(self):
        """Test form has genome field"""
        from analysisrun.forms import AnalysisRunForm

        form = AnalysisRunForm()
        assert 'genome' in form.fields

    def test_genome_field_is_required(self):
        """Test genome field is required"""
        from analysisrun.forms import AnalysisRunForm

        form = AnalysisRunForm()
        assert form.fields['genome'].required is True


class TestFormIntegration(BaseAPITestNoDatabase):
    """Test form integration"""

    def test_analysisrun_form_instantiation(self):
        """Test AnalysisRunForm can be instantiated"""
        from analysisrun.forms import AnalysisRunForm

        form = AnalysisRunForm()
        assert form is not None
        assert hasattr(form, 'fields')
