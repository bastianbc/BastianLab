# tests/unit/libprep/test_forms.py
"""
Libprep Forms Test Cases - No Database Required
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django import forms
from tests.utils.base_test import BaseAPITestNoDatabase
from tests.fixtures.libprep_fixtures import LibprepTestData


class TestNucAcidForm(BaseAPITestNoDatabase):
    """Test NucAcidForm"""

    @patch('libprep.forms.Area.objects')
    def test_form_initialization(self, mock_area_objects):
        """Test NucAcidForm initializes correctly"""
        # Setup mock
        mock_area_objects.all.return_value = MagicMock()

        from libprep.forms import NucAcidForm
        form = NucAcidForm()

        assert form is not None

    @patch('libprep.forms.Area.objects')
    def test_form_inherits_from_base_form(self, mock_area_objects):
        """Test NucAcidForm inherits from BaseForm"""
        from libprep.forms import NucAcidForm
        from core.forms import BaseForm

        assert issubclass(NucAcidForm, BaseForm)

    @patch('libprep.forms.Area.objects')
    def test_form_inherits_from_model_form(self, mock_area_objects):
        """Test NucAcidForm inherits from ModelForm"""
        from libprep.forms import NucAcidForm

        assert issubclass(NucAcidForm, forms.ModelForm)

    @patch('libprep.forms.Area.objects')
    def test_form_meta_model(self, mock_area_objects):
        """Test form Meta.model is NucAcids"""
        from libprep.forms import NucAcidForm
        from libprep.models import NucAcids

        assert NucAcidForm.Meta.model == NucAcids

    @patch('libprep.forms.Area.objects')
    def test_form_meta_fields(self, mock_area_objects):
        """Test form Meta.fields includes expected fields"""
        from libprep.forms import NucAcidForm

        expected_fields = ("name", "date", "method", "na_type", "conc", "vol_init", "vol_remain", "notes", "area",)
        assert NucAcidForm.Meta.fields == expected_fields

    @patch('libprep.forms.Area.objects')
    def test_form_has_area_field(self, mock_area_objects):
        """Test form has area field"""
        # Setup mock
        mock_area_objects.all.return_value = MagicMock()

        from libprep.forms import NucAcidForm
        form = NucAcidForm()

        assert 'area' in form.fields

    @patch('libprep.forms.Area.objects')
    def test_area_field_is_model_multiple_choice_field(self, mock_area_objects):
        """Test area field is ModelMultipleChoiceField"""
        # Setup mock
        mock_area_objects.all.return_value = MagicMock()

        from libprep.forms import NucAcidForm
        form = NucAcidForm()

        assert isinstance(form.fields['area'], forms.ModelMultipleChoiceField)

    @patch('libprep.forms.Area.objects')
    def test_form_has_amount_field(self, mock_area_objects):
        """Test form has amount field"""
        # Setup mock
        mock_area_objects.all.return_value = MagicMock()

        from libprep.forms import NucAcidForm
        form = NucAcidForm()

        assert 'amount' in form.fields

    @patch('libprep.forms.Area.objects')
    def test_amount_field_is_float_field(self, mock_area_objects):
        """Test amount field is FloatField"""
        # Setup mock
        mock_area_objects.all.return_value = MagicMock()

        from libprep.forms import NucAcidForm
        form = NucAcidForm()

        assert isinstance(form.fields['amount'], forms.FloatField)

    @patch('libprep.forms.Area.objects')
    def test_name_field_not_required(self, mock_area_objects):
        """Test name field is not required"""
        # Setup mock
        mock_area_objects.all.return_value = MagicMock()

        from libprep.forms import NucAcidForm
        form = NucAcidForm()

        assert form.fields['name'].required is False

    @patch('libprep.forms.Area.objects')
    def test_area_field_not_required(self, mock_area_objects):
        """Test area field is not required"""
        # Setup mock
        mock_area_objects.all.return_value = MagicMock()

        from libprep.forms import NucAcidForm
        form = NucAcidForm()

        assert form.fields['area'].required is False


class TestSampleLibCreationOptionsForm(BaseAPITestNoDatabase):
    """Test SampleLibCreationOptionsForm"""

    @patch('libprep.forms.Barcode.objects')
    def test_form_initialization(self, mock_barcode_objects):
        """Test SampleLibCreationOptionsForm initializes correctly"""
        # Setup mock
        mock_barcode_objects.filter.return_value = MagicMock()

        from libprep.forms import SampleLibCreationOptionsForm
        form = SampleLibCreationOptionsForm()

        assert form is not None

    @patch('libprep.forms.Barcode.objects')
    def test_form_inherits_from_forms_form(self, mock_barcode_objects):
        """Test SampleLibCreationOptionsForm inherits from forms.Form"""
        from libprep.forms import SampleLibCreationOptionsForm

        assert issubclass(SampleLibCreationOptionsForm, forms.Form)

    @patch('libprep.forms.Barcode.objects')
    def test_form_has_barcode_start_with_field(self, mock_barcode_objects):
        """Test form has barcode_start_with field"""
        # Setup mock
        mock_barcode_objects.filter.return_value = MagicMock()

        from libprep.forms import SampleLibCreationOptionsForm
        form = SampleLibCreationOptionsForm()

        assert 'barcode_start_with' in form.fields

    @patch('libprep.forms.Barcode.objects')
    def test_barcode_start_with_field_is_model_choice_field(self, mock_barcode_objects):
        """Test barcode_start_with field is ModelChoiceField"""
        # Setup mock
        mock_barcode_objects.filter.return_value = MagicMock()

        from libprep.forms import SampleLibCreationOptionsForm
        form = SampleLibCreationOptionsForm()

        assert isinstance(form.fields['barcode_start_with'], forms.ModelChoiceField)

    @patch('libprep.forms.Barcode.objects')
    def test_form_has_target_amount_field(self, mock_barcode_objects):
        """Test form has target_amount field"""
        # Setup mock
        mock_barcode_objects.filter.return_value = MagicMock()

        from libprep.forms import SampleLibCreationOptionsForm
        form = SampleLibCreationOptionsForm()

        assert 'target_amount' in form.fields

    @patch('libprep.forms.Barcode.objects')
    def test_target_amount_field_is_float_field(self, mock_barcode_objects):
        """Test target_amount field is FloatField"""
        # Setup mock
        mock_barcode_objects.filter.return_value = MagicMock()

        from libprep.forms import SampleLibCreationOptionsForm
        form = SampleLibCreationOptionsForm()

        assert isinstance(form.fields['target_amount'], forms.FloatField)

    @patch('libprep.forms.Barcode.objects')
    def test_form_has_shear_volume_field(self, mock_barcode_objects):
        """Test form has shear_volume field"""
        # Setup mock
        mock_barcode_objects.filter.return_value = MagicMock()

        from libprep.forms import SampleLibCreationOptionsForm
        form = SampleLibCreationOptionsForm()

        assert 'shear_volume' in form.fields

    @patch('libprep.forms.Barcode.objects')
    def test_shear_volume_field_is_float_field(self, mock_barcode_objects):
        """Test shear_volume field is FloatField"""
        # Setup mock
        mock_barcode_objects.filter.return_value = MagicMock()

        from libprep.forms import SampleLibCreationOptionsForm
        form = SampleLibCreationOptionsForm()

        assert isinstance(form.fields['shear_volume'], forms.FloatField)

    @patch('libprep.forms.Barcode.objects')
    def test_form_has_prefix_field(self, mock_barcode_objects):
        """Test form has prefix field"""
        # Setup mock
        mock_barcode_objects.filter.return_value = MagicMock()

        from libprep.forms import SampleLibCreationOptionsForm
        form = SampleLibCreationOptionsForm()

        assert 'prefix' in form.fields

    @patch('libprep.forms.Barcode.objects')
    def test_prefix_field_is_char_field(self, mock_barcode_objects):
        """Test prefix field is CharField"""
        # Setup mock
        mock_barcode_objects.filter.return_value = MagicMock()

        from libprep.forms import SampleLibCreationOptionsForm
        form = SampleLibCreationOptionsForm()

        assert isinstance(form.fields['prefix'], forms.CharField)


class TestFilterForm(BaseAPITestNoDatabase):
    """Test FilterForm"""

    def test_form_initialization(self):
        """Test FilterForm initializes correctly"""
        from libprep.forms import FilterForm
        form = FilterForm()

        assert form is not None

    def test_form_inherits_from_forms_form(self):
        """Test FilterForm inherits from forms.Form"""
        from libprep.forms import FilterForm

        assert issubclass(FilterForm, forms.Form)

    def test_form_has_date_range_field(self):
        """Test form has date_range field"""
        from libprep.forms import FilterForm
        form = FilterForm()

        assert 'date_range' in form.fields

    def test_date_range_field_is_date_field(self):
        """Test date_range field is DateField"""
        from libprep.forms import FilterForm
        form = FilterForm()

        assert isinstance(form.fields['date_range'], forms.DateField)

    def test_form_has_na_type_field(self):
        """Test form has na_type field"""
        from libprep.forms import FilterForm
        form = FilterForm()

        assert 'na_type' in form.fields

    def test_na_type_field_is_choice_field(self):
        """Test na_type field is ChoiceField"""
        from libprep.forms import FilterForm
        form = FilterForm()

        assert isinstance(form.fields['na_type'], forms.ChoiceField)

    def test_na_type_field_not_required(self):
        """Test na_type field is not required"""
        from libprep.forms import FilterForm
        form = FilterForm()

        assert form.fields['na_type'].required is False

    def test_date_range_field_has_css_class(self):
        """Test date_range field has form-control-sm class"""
        from libprep.forms import FilterForm
        form = FilterForm()

        assert 'form-control-sm' in form.fields['date_range'].widget.attrs.get('class', '')

    def test_na_type_field_has_css_class(self):
        """Test na_type field has form-control-sm class"""
        from libprep.forms import FilterForm
        form = FilterForm()

        assert 'form-control-sm' in form.fields['na_type'].widget.attrs.get('class', '')


class TestFormIntegration(BaseAPITestNoDatabase):
    """Integration tests for forms"""

    @patch('libprep.forms.Area.objects')
    def test_nucacid_form_instantiation(self, mock_area_objects):
        """Test NucAcidForm can be instantiated"""
        # Setup mock
        mock_area_objects.all.return_value = MagicMock()

        from libprep.forms import NucAcidForm

        form = NucAcidForm()
        assert form is not None

    @patch('libprep.forms.Barcode.objects')
    def test_samplelib_options_form_instantiation(self, mock_barcode_objects):
        """Test SampleLibCreationOptionsForm can be instantiated"""
        # Setup mock
        mock_barcode_objects.filter.return_value = MagicMock()

        from libprep.forms import SampleLibCreationOptionsForm

        form = SampleLibCreationOptionsForm()
        assert form is not None

    def test_filter_form_instantiation(self):
        """Test FilterForm can be instantiated"""
        from libprep.forms import FilterForm

        form = FilterForm()
        assert form is not None
