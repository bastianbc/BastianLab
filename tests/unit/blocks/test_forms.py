# tests/unit/blocks/test_forms.py
"""
Blocks Forms Test Cases - No Database Required
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django import forms
from tests.utils.base_test import BaseAPITestNoDatabase
from tests.fixtures.blocks_fixtures import BlocksTestData


class TestBlockForm(BaseAPITestNoDatabase):
    """Test BlockForm"""

    @patch('blocks.forms.Patient.objects')
    @patch('blocks.forms.Project.objects')
    def test_form_initialization(self, mock_project_objects, mock_patient_objects):
        """Test BlockForm initializes correctly"""
        # Setup mocks
        mock_patient_objects.all.return_value.order_by.return_value = MagicMock()
        mock_project_objects.all.return_value.order_by.return_value = MagicMock()

        from blocks.forms import BlockForm
        form = BlockForm()

        # Verify form initializes successfully
        assert form is not None

    @patch('blocks.forms.Patient.objects')
    @patch('blocks.forms.Project.objects')
    def test_form_has_projects_field(self, mock_project_objects, mock_patient_objects):
        """Test form has projects field"""
        # Setup mocks
        mock_patient_objects.all.return_value.order_by.return_value = MagicMock()
        mock_project_objects.all.return_value.order_by.return_value = MagicMock()

        from blocks.forms import BlockForm
        form = BlockForm()

        assert 'projects' in form.fields

    @patch('blocks.forms.Patient.objects')
    @patch('blocks.forms.Project.objects')
    def test_form_inherits_from_base_form(self, mock_project_objects, mock_patient_objects):
        """Test BlockForm inherits from BaseForm"""
        from blocks.forms import BlockForm
        from core.forms import BaseForm

        assert issubclass(BlockForm, BaseForm)

    @patch('blocks.forms.Patient.objects')
    @patch('blocks.forms.Project.objects')
    def test_form_inherits_from_model_form(self, mock_project_objects, mock_patient_objects):
        """Test BlockForm inherits from ModelForm"""
        from blocks.forms import BlockForm

        assert issubclass(BlockForm, forms.ModelForm)

    @patch('blocks.forms.Patient.objects')
    @patch('blocks.forms.Project.objects')
    def test_form_meta_model(self, mock_project_objects, mock_patient_objects):
        """Test form Meta.model is Block"""
        from blocks.forms import BlockForm
        from blocks.models import Block

        assert BlockForm.Meta.model == Block

    @patch('blocks.forms.Patient.objects')
    @patch('blocks.forms.Project.objects')
    def test_form_meta_fields_all(self, mock_project_objects, mock_patient_objects):
        """Test form Meta.fields is __all__"""
        from blocks.forms import BlockForm

        assert BlockForm.Meta.fields == "__all__"

    @patch('blocks.forms.Patient.objects')
    @patch('blocks.forms.Project.objects')
    def test_form_body_site_widget_hidden(self, mock_project_objects, mock_patient_objects):
        """Test body_site field uses HiddenInput widget"""
        # Setup mocks
        mock_patient_objects.all.return_value.order_by.return_value = MagicMock()
        mock_project_objects.all.return_value.order_by.return_value = MagicMock()

        from blocks.forms import BlockForm
        form = BlockForm()

        # body_site should have HiddenInput widget
        assert isinstance(form.fields['body_site'].widget, forms.HiddenInput)

    @patch('blocks.forms.Patient.objects')
    @patch('blocks.forms.Project.objects')
    def test_form_diagnosis_widget_is_textarea(self, mock_project_objects, mock_patient_objects):
        """Test diagnosis field uses Textarea widget"""
        # Setup mocks
        mock_patient_objects.all.return_value.order_by.return_value = MagicMock()
        mock_project_objects.all.return_value.order_by.return_value = MagicMock()

        from blocks.forms import BlockForm
        form = BlockForm()

        # diagnosis should have Textarea widget
        assert isinstance(form.fields['diagnosis'].widget, forms.Textarea)

    @patch('blocks.forms.Patient.objects')
    @patch('blocks.forms.Project.objects')
    def test_clean_body_site_returns_none_for_empty(self, mock_project_objects, mock_patient_objects):
        """Test clean_body_site returns None for empty value"""
        # Setup mocks
        mock_patient_objects.all.return_value.order_by.return_value = MagicMock()
        mock_project_objects.all.return_value.order_by.return_value = MagicMock()

        from blocks.forms import BlockForm
        form = BlockForm()
        form.cleaned_data = {'body_site': None}

        result = form.clean_body_site()
        assert result is None


class TestAreaCreationForm(BaseAPITestNoDatabase):
    """Test AreaCreationForm"""

    def test_form_initialization(self):
        """Test AreaCreationForm initializes correctly"""
        from blocks.forms import AreaCreationForm
        form = AreaCreationForm()

        assert form is not None

    def test_form_has_number_field(self):
        """Test form has number field"""
        from blocks.forms import AreaCreationForm
        form = AreaCreationForm()

        assert 'number' in form.fields

    def test_number_field_is_integer_field(self):
        """Test number field is IntegerField"""
        from blocks.forms import AreaCreationForm
        form = AreaCreationForm()

        assert isinstance(form.fields['number'], forms.IntegerField)

    def test_number_field_initial_value(self):
        """Test number field has initial value of 1"""
        from blocks.forms import AreaCreationForm
        form = AreaCreationForm()

        assert form.fields['number'].initial == 1

    def test_number_field_label(self):
        """Test number field has correct label"""
        from blocks.forms import AreaCreationForm
        form = AreaCreationForm()

        assert form.fields['number'].label == "How many areas for block do you want to create?"

    def test_form_inherits_from_forms_form(self):
        """Test AreaCreationForm inherits from forms.Form"""
        from blocks.forms import AreaCreationForm

        assert issubclass(AreaCreationForm, forms.Form)


class TestBlockUrlForm(BaseAPITestNoDatabase):
    """Test BlockUrlForm"""

    def test_form_initialization(self):
        """Test BlockUrlForm initializes correctly"""
        from blocks.forms import BlockUrlForm
        form = BlockUrlForm()

        assert form is not None

    def test_form_meta_model(self):
        """Test form Meta.model is BlockUrl"""
        from blocks.forms import BlockUrlForm
        from blocks.models import BlockUrl

        assert BlockUrlForm.Meta.model == BlockUrl

    def test_form_meta_fields_all(self):
        """Test form Meta.fields is __all__"""
        from blocks.forms import BlockUrlForm

        assert BlockUrlForm.Meta.fields == "__all__"

    def test_form_inherits_from_model_form(self):
        """Test BlockUrlForm inherits from ModelForm"""
        from blocks.forms import BlockUrlForm

        assert issubclass(BlockUrlForm, forms.ModelForm)

    def test_clean_url_with_trailing_slash(self):
        """Test clean_url accepts URL with trailing slash"""
        from blocks.forms import BlockUrlForm

        form = BlockUrlForm(data={'url': 'http://example.com/'})
        is_valid = form.is_valid()

        # Should be valid with trailing slash
        assert is_valid is True

    def test_clean_url_without_trailing_slash(self):
        """Test clean_url raises error for URL without trailing slash"""
        from blocks.forms import BlockUrlForm

        form = BlockUrlForm(data={'url': 'http://example.com'})
        is_valid = form.is_valid()

        # Should be invalid without trailing slash
        assert is_valid is False
        assert 'url' in form.errors


class TestFilterForm(BaseAPITestNoDatabase):
    """Test FilterForm"""

    @patch('blocks.forms.Body.objects')
    def test_form_initialization(self, mock_body_objects):
        """Test FilterForm initializes correctly"""
        # Setup mock
        mock_body_objects.all.return_value = MagicMock()

        from blocks.forms import FilterForm
        form = FilterForm()

        assert form is not None

    @patch('blocks.forms.Body.objects')
    def test_form_has_all_fields(self, mock_body_objects):
        """Test form has all expected fields"""
        # Setup mock
        mock_body_objects.all.return_value = MagicMock()

        from blocks.forms import FilterForm
        form = FilterForm()

        assert 'p_stage' in form.fields
        assert 'prim' in form.fields
        assert 'body_site' in form.fields

    @patch('blocks.forms.Body.objects')
    def test_p_stage_field_is_choice_field(self, mock_body_objects):
        """Test p_stage field is ChoiceField"""
        # Setup mock
        mock_body_objects.all.return_value = MagicMock()

        from blocks.forms import FilterForm
        form = FilterForm()

        assert isinstance(form.fields['p_stage'], forms.ChoiceField)

    @patch('blocks.forms.Body.objects')
    def test_prim_field_is_choice_field(self, mock_body_objects):
        """Test prim field is ChoiceField"""
        # Setup mock
        mock_body_objects.all.return_value = MagicMock()

        from blocks.forms import FilterForm
        form = FilterForm()

        assert isinstance(form.fields['prim'], forms.ChoiceField)

    @patch('blocks.forms.Body.objects')
    def test_body_site_field_is_model_choice_field(self, mock_body_objects):
        """Test body_site field is ModelChoiceField"""
        # Setup mock
        mock_body_objects.all.return_value = MagicMock()

        from blocks.forms import FilterForm
        form = FilterForm()

        assert isinstance(form.fields['body_site'], forms.ModelChoiceField)

    @patch('blocks.forms.Body.objects')
    def test_p_stage_field_not_required(self, mock_body_objects):
        """Test p_stage field is not required"""
        # Setup mock
        mock_body_objects.all.return_value = MagicMock()

        from blocks.forms import FilterForm
        form = FilterForm()

        assert form.fields['p_stage'].required is False

    @patch('blocks.forms.Body.objects')
    def test_prim_field_not_required(self, mock_body_objects):
        """Test prim field is not required"""
        # Setup mock
        mock_body_objects.all.return_value = MagicMock()

        from blocks.forms import FilterForm
        form = FilterForm()

        assert form.fields['prim'].required is False

    @patch('blocks.forms.Body.objects')
    def test_form_inherits_from_forms_form(self, mock_body_objects):
        """Test FilterForm inherits from forms.Form"""
        from blocks.forms import FilterForm

        assert issubclass(FilterForm, forms.Form)

    @patch('blocks.forms.Body.objects')
    def test_p_stage_includes_empty_option(self, mock_body_objects):
        """Test p_stage field includes empty option"""
        # Setup mock
        mock_body_objects.all.return_value = MagicMock()

        from blocks.forms import FilterForm
        form = FilterForm()

        # First choice should be empty
        choices = form.fields['p_stage'].choices
        assert choices[0] == ('', '---------')

    @patch('blocks.forms.Body.objects')
    def test_prim_includes_empty_option(self, mock_body_objects):
        """Test prim field includes empty option"""
        # Setup mock
        mock_body_objects.all.return_value = MagicMock()

        from blocks.forms import FilterForm
        form = FilterForm()

        # First choice should be empty
        choices = form.fields['prim'].choices
        assert choices[0] == ('', '---------')

    @patch('blocks.forms.Body.objects')
    def test_form_widget_attrs(self, mock_body_objects):
        """Test form fields have correct widget attributes"""
        # Setup mock
        mock_body_objects.all.return_value = MagicMock()

        from blocks.forms import FilterForm
        form = FilterForm()

        # Check widget attributes
        assert 'form-control-sm' in form.fields['p_stage'].widget.attrs.get('class', '')
        assert 'form-control-sm' in form.fields['prim'].widget.attrs.get('class', '')
        assert 'form-control-sm' in form.fields['body_site'].widget.attrs.get('class', '')
        assert form.fields['body_site'].widget.attrs.get('data-control') == 'select2'


class TestFormIntegration(BaseAPITestNoDatabase):
    """Integration tests for forms"""

    @patch('blocks.forms.Patient.objects')
    @patch('blocks.forms.Project.objects')
    def test_block_form_with_data(self, mock_project_objects, mock_patient_objects):
        """Test BlockForm with data"""
        # Setup mocks
        mock_patient_objects.all.return_value.order_by.return_value = MagicMock()
        mock_project_objects.all.return_value.order_by.return_value = MagicMock()

        from blocks.forms import BlockForm

        # Form should be instantiated
        form = BlockForm()
        assert form is not None

    def test_area_creation_form_with_data(self):
        """Test AreaCreationForm with valid data"""
        from blocks.forms import AreaCreationForm

        data = {'number': 5}
        form = AreaCreationForm(data=data)

        # Form should be valid
        assert form.is_valid() is True

    def test_block_url_form_with_valid_data(self):
        """Test BlockUrlForm with valid data"""
        from blocks.forms import BlockUrlForm

        data = {'url': 'http://example.com/'}
        form = BlockUrlForm(data=data)

        # Form should be valid
        assert form.is_valid() is True

    @patch('blocks.forms.Body.objects')
    def test_filter_form_with_data(self, mock_body_objects):
        """Test FilterForm with data"""
        # Setup mock
        mock_body_objects.all.return_value = MagicMock()

        from blocks.forms import FilterForm

        form = FilterForm()
        assert form is not None
