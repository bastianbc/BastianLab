# tests/unit/areas/test_forms.py
"""
Areas Forms Test Cases - No Database Required
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django import forms
from tests.utils.base_test import BaseAPITestNoDatabase
from tests.fixtures.areas_fixtures import AreasTestData


class TestAreaForm(BaseAPITestNoDatabase):
    """Test AreaForm"""

    @patch('areas.forms.AreaType.objects')
    def test_form_initialization(self, mock_areatype_objects):
        """Test AreaForm initializes correctly"""
        # Setup mock
        mock_areatype_objects.all.return_value.order_by.return_value = MagicMock()

        from areas.forms import AreaForm
        form = AreaForm()

        assert form is not None

    @patch('areas.forms.AreaType.objects')
    def test_form_inherits_from_base_form(self, mock_areatype_objects):
        """Test AreaForm inherits from BaseForm"""
        from areas.forms import AreaForm
        from core.forms import BaseForm

        assert issubclass(AreaForm, BaseForm)

    @patch('areas.forms.AreaType.objects')
    def test_form_inherits_from_model_form(self, mock_areatype_objects):
        """Test AreaForm inherits from ModelForm"""
        from areas.forms import AreaForm

        assert issubclass(AreaForm, forms.ModelForm)

    @patch('areas.forms.AreaType.objects')
    def test_form_meta_model(self, mock_areatype_objects):
        """Test form Meta.model is Area"""
        from areas.forms import AreaForm
        from areas.models import Area

        assert AreaForm.Meta.model == Area

    @patch('areas.forms.AreaType.objects')
    def test_form_meta_fields_all(self, mock_areatype_objects):
        """Test form Meta.fields is __all__"""
        from areas.forms import AreaForm

        assert AreaForm.Meta.fields == "__all__"

    @patch('areas.forms.AreaType.objects')
    def test_form_block_field_has_select2(self, mock_areatype_objects):
        """Test block field has select2 data-control"""
        # Setup mock
        mock_areatype_objects.all.return_value.order_by.return_value = MagicMock()

        from areas.forms import AreaForm
        form = AreaForm()

        assert form.fields['block'].widget.attrs.get('data-control') == 'select2'

    @patch('areas.forms.AreaType.objects')
    def test_form_block_field_has_css_class(self, mock_areatype_objects):
        """Test block field has form-control-sm class"""
        # Setup mock
        mock_areatype_objects.all.return_value.order_by.return_value = MagicMock()

        from areas.forms import AreaForm
        form = AreaForm()

        assert 'form-control-sm' in form.fields['block'].widget.attrs.get('class', '')

    @patch('areas.forms.AreaType.objects')
    def test_form_area_type_field_has_select2(self, mock_areatype_objects):
        """Test area_type field has select2 data-control"""
        # Setup mock
        mock_areatype_objects.all.return_value.order_by.return_value = MagicMock()

        from areas.forms import AreaForm
        form = AreaForm()

        assert form.fields['area_type'].widget.attrs.get('data-control') == 'select2'

    @patch('areas.forms.AreaType.objects')
    def test_form_area_type_field_queryset_ordered(self, mock_areatype_objects):
        """Test area_type field queryset is ordered"""
        # Setup mock
        mock_queryset = MagicMock()
        mock_areatype_objects.all.return_value.order_by.return_value = mock_queryset

        from areas.forms import AreaForm
        form = AreaForm()

        # Verify that order_by was called with 'name'
        mock_areatype_objects.all.return_value.order_by.assert_called_with('name')


class TestExtractionOptionsForm(BaseAPITestNoDatabase):
    """Test ExtractionOptionsForm"""

    def test_form_initialization(self):
        """Test ExtractionOptionsForm initializes correctly"""
        with patch('areas.forms.Method.objects') as mock_method_objects:
            mock_method_objects.all.return_value = MagicMock()

            from areas.forms import ExtractionOptionsForm
            form = ExtractionOptionsForm()

            assert form is not None

    def test_form_has_na_type_field(self):
        """Test form has na_type field"""
        with patch('areas.forms.Method.objects') as mock_method_objects:
            mock_method_objects.all.return_value = MagicMock()

            from areas.forms import ExtractionOptionsForm
            form = ExtractionOptionsForm()

            assert 'na_type' in form.fields

    def test_na_type_field_is_choice_field(self):
        """Test na_type field is ChoiceField"""
        with patch('areas.forms.Method.objects') as mock_method_objects:
            mock_method_objects.all.return_value = MagicMock()

            from areas.forms import ExtractionOptionsForm
            form = ExtractionOptionsForm()

            assert isinstance(form.fields['na_type'], forms.ChoiceField)

    def test_form_has_extraction_method_field(self):
        """Test form has extraction_method field"""
        with patch('areas.forms.Method.objects') as mock_method_objects:
            mock_method_objects.all.return_value = MagicMock()

            from areas.forms import ExtractionOptionsForm
            form = ExtractionOptionsForm()

            assert 'extraction_method' in form.fields

    def test_extraction_method_field_is_model_choice_field(self):
        """Test extraction_method field is ModelChoiceField"""
        with patch('areas.forms.Method.objects') as mock_method_objects:
            mock_method_objects.all.return_value = MagicMock()

            from areas.forms import ExtractionOptionsForm
            form = ExtractionOptionsForm()

            assert isinstance(form.fields['extraction_method'], forms.ModelChoiceField)

    def test_form_inherits_from_forms_form(self):
        """Test ExtractionOptionsForm inherits from forms.Form"""
        from areas.forms import ExtractionOptionsForm

        assert issubclass(ExtractionOptionsForm, forms.Form)


class TestFormIntegration(BaseAPITestNoDatabase):
    """Integration tests for forms"""

    @patch('areas.forms.AreaType.objects')
    def test_area_form_instantiation(self, mock_areatype_objects):
        """Test AreaForm can be instantiated"""
        # Setup mock
        mock_areatype_objects.all.return_value.order_by.return_value = MagicMock()

        from areas.forms import AreaForm

        form = AreaForm()
        assert form is not None

    def test_extraction_options_form_instantiation(self):
        """Test ExtractionOptionsForm can be instantiated"""
        with patch('areas.forms.Method.objects') as mock_method_objects:
            mock_method_objects.all.return_value = MagicMock()

            from areas.forms import ExtractionOptionsForm

            form = ExtractionOptionsForm()
            assert form is not None
