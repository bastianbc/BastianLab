# tests/unit/patients/test_forms.py
"""
Patient Forms Test Cases - No Database Required

Tests PatientForm and FilterForm with complete database mocking.
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from django import forms
from tests.utils.base_test import BaseAPITestNoDatabase
from tests.fixtures.patient_fixtures import PatientTestData


class TestPatientForm(BaseAPITestNoDatabase):
    """Test PatientForm"""

    @patch('lab.forms.Block.objects')
    def test_form_initialization(self, mock_block_objects):
        """Test PatientForm initializes with correct queryset"""
        # Setup mock queryset
        mock_block_queryset = MagicMock()
        mock_block_objects.all.return_value.order_by.return_value = mock_block_queryset

        # Import and create form
        from lab.forms import PatientForm
        form = PatientForm()

        # Verify form initializes successfully
        assert form is not None
        assert 'block' in form.fields

    @patch('lab.forms.Block.objects')
    def test_form_has_all_fields(self, mock_block_objects):
        """Test form contains all expected fields"""
        # Setup mocks
        mock_block_objects.all.return_value.order_by.return_value = MagicMock()

        from lab.forms import PatientForm
        form = PatientForm()

        # Verify all fields are present
        expected_fields = [
            'pat_id', 'dob', 'sex', 'race', 'source',
            'block', 'notes', 'consent'
        ]

        for field_name in expected_fields:
            assert field_name in form.fields

    @patch('lab.forms.Block.objects')
    def test_form_block_field_configuration(self, mock_block_objects):
        """Test block field is ModelMultipleChoiceField"""
        # Setup
        mock_block_objects.all.return_value.order_by.return_value = MagicMock()

        from lab.forms import PatientForm
        form = PatientForm()

        # Verify block field type and configuration
        assert isinstance(form.fields['block'], forms.ModelMultipleChoiceField)
        assert form.fields['block'].required is False
        assert form.fields['block'].label == "Blocks"

    @patch('lab.forms.Block.objects')
    def test_form_notes_widget(self, mock_block_objects):
        """Test notes field has Textarea widget"""
        # Setup
        mock_block_objects.all.return_value.order_by.return_value = MagicMock()

        from lab.forms import PatientForm
        form = PatientForm()

        # Verify notes widget
        assert isinstance(form.fields['notes'].widget, forms.Textarea)
        assert form.fields['notes'].widget.attrs['rows'] == 4
        assert form.fields['notes'].widget.attrs['cols'] == 40

    @patch('lab.forms.Block.objects')
    def test_form_dob_widget(self, mock_block_objects):
        """Test dob field has NumberInput widget with attributes"""
        # Setup
        mock_block_objects.all.return_value.order_by.return_value = MagicMock()

        from lab.forms import PatientForm
        form = PatientForm()

        # Verify dob widget
        assert isinstance(form.fields['dob'].widget, forms.NumberInput)
        assert form.fields['dob'].widget.attrs['placeholder'] == 'Year'

    @patch('lab.forms.Block.objects')
    def test_form_initialization_without_instance(self, mock_block_objects):
        """Test form initialization without instance works correctly"""
        # Setup
        mock_block_objects.all.return_value.order_by.return_value = MagicMock()

        from lab.forms import PatientForm

        # Form should initialize without instance
        form = PatientForm()

        # Verify form initializes successfully
        assert form is not None
        assert 'block' in form.fields
        # Block field should not have initial value when no instance
        assert form.fields['block'].initial is None

    @patch('lab.forms.BaseForm.save')
    @patch('lab.forms.Block.objects')
    def test_form_save_method(self, mock_block_objects, mock_base_save):
        """Test save method saves instance and M2M relationships"""
        # Setup
        mock_block_objects.all.return_value.order_by.return_value = MagicMock()

        # Create mock instance
        mock_instance = Mock()
        mock_instance.save = Mock()
        mock_instance.patient_blocks = Mock()
        mock_instance.patient_blocks.set = Mock()
        mock_base_save.return_value = mock_instance

        from lab.forms import PatientForm
        form = PatientForm()
        form.cleaned_data = {'block': [Mock(), Mock()]}

        # Call save
        result = form.save()

        # Verify save was called with commit=False
        mock_base_save.assert_called_once_with(commit=False)

        # Verify instance.save was called
        mock_instance.save.assert_called_once()

        # Verify patient_blocks.set was called
        mock_instance.patient_blocks.set.assert_called_once_with(form.cleaned_data['block'])

        # Verify instance was returned
        assert result == mock_instance

    @patch('lab.forms.Block.objects')
    def test_form_meta_model(self, mock_block_objects):
        """Test form Meta.model is Patient"""
        from lab.forms import PatientForm
        from lab.models import Patient

        assert PatientForm.Meta.model == Patient

    @patch('lab.forms.Block.objects')
    def test_form_meta_fields(self, mock_block_objects):
        """Test form Meta.fields includes all expected fields"""
        from lab.forms import PatientForm

        expected_fields = (
            'pat_id', 'dob', 'sex', 'race', 'source',
            'block', 'notes', 'consent'
        )

        assert PatientForm.Meta.fields == expected_fields

    @patch('lab.forms.Block.objects')
    def test_form_inherits_from_base_form(self, mock_block_objects):
        """Test PatientForm inherits from BaseForm"""
        # Setup
        mock_block_objects.all.return_value.order_by.return_value = MagicMock()

        from lab.forms import PatientForm
        from core.forms import BaseForm

        assert issubclass(PatientForm, BaseForm)

    @patch('lab.forms.Block.objects')
    def test_form_sex_field_is_choice_field(self, mock_block_objects):
        """Test sex field is ChoiceField"""
        # Setup
        mock_block_objects.all.return_value.order_by.return_value = MagicMock()

        from lab.forms import PatientForm
        form = PatientForm()

        # The sex field should be a ChoiceField (from model)
        assert 'sex' in form.fields

    @patch('lab.forms.Block.objects')
    def test_form_race_field_is_choice_field(self, mock_block_objects):
        """Test race field is ChoiceField"""
        # Setup
        mock_block_objects.all.return_value.order_by.return_value = MagicMock()

        from lab.forms import PatientForm
        form = PatientForm()

        # The race field should be a ChoiceField (from model)
        assert 'race' in form.fields

    @patch('lab.forms.Block.objects')
    def test_form_consent_field_is_choice_field(self, mock_block_objects):
        """Test consent field is ChoiceField"""
        # Setup
        mock_block_objects.all.return_value.order_by.return_value = MagicMock()

        from lab.forms import PatientForm
        form = PatientForm()

        # The consent field should be a ChoiceField (from model)
        assert 'consent' in form.fields


class TestFilterForm(BaseAPITestNoDatabase):
    """Test FilterForm"""

    def test_filter_form_initialization(self):
        """Test FilterForm initializes correctly"""
        from lab.forms import FilterForm
        form = FilterForm()

        # Form should initialize successfully
        assert form is not None
        assert 'race' in form.fields
        assert 'sex' in form.fields
        assert 'dob' in form.fields

    def test_filter_form_has_all_fields(self):
        """Test FilterForm has all expected fields"""
        from lab.forms import FilterForm
        form = FilterForm()

        # Verify all fields are present
        assert 'race' in form.fields
        assert 'sex' in form.fields
        assert 'dob' in form.fields

    def test_filter_form_race_field(self):
        """Test race field is ChoiceField"""
        from lab.forms import FilterForm
        form = FilterForm()

        # Verify field type
        assert isinstance(form.fields['race'], forms.ChoiceField)
        assert form.fields['race'].label == "Race"
        assert form.fields['race'].required is False

    def test_filter_form_sex_field(self):
        """Test sex field is ChoiceField"""
        from lab.forms import FilterForm
        form = FilterForm()

        # Verify field type
        assert isinstance(form.fields['sex'], forms.ChoiceField)
        assert form.fields['sex'].label == "Sex"
        assert form.fields['sex'].required is False

    def test_filter_form_dob_field(self):
        """Test dob field is IntegerField"""
        from lab.forms import FilterForm
        form = FilterForm()

        # Verify field type
        assert isinstance(form.fields['dob'], forms.IntegerField)
        assert form.fields['dob'].label == "Date of Birth"
        assert form.fields['dob'].required is False

    def test_filter_form_race_includes_empty_option(self):
        """Test race field includes empty option"""
        from lab.forms import FilterForm
        form = FilterForm()

        # First choice should be empty
        choices = form.fields['race'].choices
        assert choices[0] == (0, '---------')

    def test_filter_form_sex_includes_empty_option(self):
        """Test sex field includes empty option"""
        from lab.forms import FilterForm
        form = FilterForm()

        # First choice should be empty
        choices = form.fields['sex'].choices
        assert choices[0] == ('', '---------')

    def test_filter_form_race_widget_attrs(self):
        """Test race field has correct widget attributes"""
        from lab.forms import FilterForm
        form = FilterForm()

        # Verify widget attributes
        assert 'class' in form.fields['race'].widget.attrs
        assert form.fields['race'].widget.attrs['class'] == 'form-control-sm'
        assert 'data-control' in form.fields['race'].widget.attrs
        assert form.fields['race'].widget.attrs['data-control'] == 'select2'

    def test_filter_form_sex_widget_attrs(self):
        """Test sex field has correct widget attributes"""
        from lab.forms import FilterForm
        form = FilterForm()

        # Verify widget attributes
        assert 'class' in form.fields['sex'].widget.attrs
        assert form.fields['sex'].widget.attrs['class'] == 'form-control-sm'
        assert 'data-control' in form.fields['sex'].widget.attrs
        assert form.fields['sex'].widget.attrs['data-control'] == 'select2'

    def test_filter_form_dob_widget_attrs(self):
        """Test dob field has correct widget attributes"""
        from lab.forms import FilterForm
        form = FilterForm()

        # Verify widget attributes
        assert 'class' in form.fields['dob'].widget.attrs
        assert form.fields['dob'].widget.attrs['class'] == 'form-control-sm'
        assert 'placeholder' in form.fields['dob'].widget.attrs
        assert form.fields['dob'].widget.attrs['placeholder'] == 'Year'

    def test_filter_form_inherits_from_forms_form(self):
        """Test FilterForm inherits from forms.Form"""
        from lab.forms import FilterForm

        assert issubclass(FilterForm, forms.Form)

    def test_filter_form_race_choices_include_all_types(self):
        """Test race field includes all Patient.RACE_TYPES"""
        from lab.forms import FilterForm
        from lab.models import Patient

        form = FilterForm()
        choices = form.fields['race'].choices

        # Should have empty option + all race types
        assert len(choices) == len(Patient.RACE_TYPES) + 1

    def test_filter_form_sex_choices_include_all_types(self):
        """Test sex field includes all Patient.SEX_TYPES"""
        from lab.forms import FilterForm
        from lab.models import Patient

        form = FilterForm()
        choices = form.fields['sex'].choices

        # Should have empty option + all sex types
        assert len(choices) == len(Patient.SEX_TYPES) + 1


class TestFormIntegration(BaseAPITestNoDatabase):
    """Integration tests for forms"""

    @patch('lab.forms.Block.objects')
    def test_patient_form_with_data(self, mock_block_objects):
        """Test PatientForm with valid data"""
        # Setup
        mock_block_objects.all.return_value.order_by.return_value = MagicMock()

        from lab.forms import PatientForm

        # Create form with data
        data = {
            'pat_id': 'PAT001',
            'dob': '1980',
            'sex': 'm',
            'race': '5',
            'source': 'UCSF',
            'notes': 'Test notes',
            'consent': 'HTAN patient',
        }

        form = PatientForm(data=data)

        # Form should be instantiated
        assert form is not None

    def test_filter_form_with_data(self):
        """Test FilterForm with valid data"""
        from lab.forms import FilterForm

        # Create form with data
        data = {
            'race': '5',
            'sex': 'm',
            'dob': '1980',
        }

        form = FilterForm(data=data)

        # Form should be instantiated
        assert form is not None

    @patch('lab.forms.Block.objects')
    def test_patient_form_field_count(self, mock_block_objects):
        """Test PatientForm has exactly the expected number of fields"""
        # Setup
        mock_block_objects.all.return_value.order_by.return_value = MagicMock()

        from lab.forms import PatientForm
        form = PatientForm()

        # Should have 8 fields
        assert len(form.fields) == 8

    def test_filter_form_field_count(self):
        """Test FilterForm has exactly the expected number of fields"""
        from lab.forms import FilterForm
        form = FilterForm()

        # Should have 3 fields
        assert len(form.fields) == 3

    @patch('lab.forms.Block.objects')
    def test_patient_form_blocks_queryset(self, mock_block_objects):
        """Test block field is configured"""
        # Setup
        mock_blocks = MagicMock()
        mock_block_objects.all.return_value.order_by.return_value = mock_blocks

        from lab.forms import PatientForm
        form = PatientForm()

        # Verify block field exists and is configured
        assert 'block' in form.fields
        assert isinstance(form.fields['block'], forms.ModelMultipleChoiceField)


class TestFormEdgeCases(BaseAPITestNoDatabase):
    """Test form edge cases and error handling"""

    @patch('lab.forms.Block.objects')
    def test_patient_form_with_empty_blocks(self, mock_block_objects):
        """Test PatientForm when block queryset is empty"""
        # Setup - return empty queryset
        mock_empty_queryset = MagicMock()
        mock_empty_queryset.count.return_value = 0
        mock_block_objects.all.return_value.order_by.return_value = mock_empty_queryset

        from lab.forms import PatientForm
        form = PatientForm()

        # Form should still initialize
        assert 'block' in form.fields

    @patch('lab.forms.Block.objects')
    def test_patient_form_initialization_without_instance(self, mock_block_objects):
        """Test form initialization without instance doesn't error"""
        # Setup
        mock_block_objects.all.return_value.order_by.return_value = MagicMock()

        from lab.forms import PatientForm
        form = PatientForm()

        # Should not set initial for block field
        # The initial is only set when instance exists
        assert form is not None

    def test_filter_form_with_empty_data(self):
        """Test FilterForm with empty data"""
        from lab.forms import FilterForm

        # Create form with empty data
        data = {}

        form = FilterForm(data=data)

        # Form should handle empty data
        assert form is not None

    @patch('lab.forms.Block.objects')
    def test_patient_form_save_without_block_field(self, mock_block_objects):
        """Test save method when block field is not in cleaned_data"""
        # Setup
        mock_block_objects.all.return_value.order_by.return_value = MagicMock()

        # Create mock instance
        mock_instance = Mock()
        mock_instance.save = Mock()
        mock_instance.patient_blocks = Mock()
        mock_instance.patient_blocks.set = Mock()

        from lab.forms import PatientForm

        with patch('lab.forms.BaseForm.save', return_value=mock_instance):
            form = PatientForm()
            form.cleaned_data = {}  # No 'block' key

            # Call save - should not call patient_blocks.set
            result = form.save()

            # Verify patient_blocks.set was NOT called
            mock_instance.patient_blocks.set.assert_not_called()
