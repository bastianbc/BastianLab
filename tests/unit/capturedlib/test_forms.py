# tests/unit/capturedlib/test_forms.py
"""
Capturedlib Forms Test Cases - No Database Required
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django import forms
from tests.utils.base_test import BaseAPITestNoDatabase
from tests.fixtures.capturedlib_fixtures import CapturedlibTestData


class TestCapturedLibForm(BaseAPITestNoDatabase):
    """Test CapturedLibForm"""

    @patch('capturedlib.forms.SampleLib.objects')
    def test_form_initialization(self, mock_sl_objects):
        """Test CapturedLibForm initializes correctly"""
        mock_sl_objects.all.return_value = MagicMock()
        from capturedlib.forms import CapturedLibForm

        form = CapturedLibForm()
        assert form is not None

    @patch('capturedlib.forms.SampleLib.objects')
    def test_form_inherits_from_model_form(self, mock_sl_objects):
        """Test CapturedLibForm inherits from ModelForm"""
        mock_sl_objects.all.return_value = MagicMock()
        from capturedlib.forms import CapturedLibForm

        assert issubclass(CapturedLibForm, forms.ModelForm)

    @patch('capturedlib.forms.SampleLib.objects')
    def test_form_inherits_from_base_form(self, mock_sl_objects):
        """Test CapturedLibForm inherits from BaseForm"""
        mock_sl_objects.all.return_value = MagicMock()
        from capturedlib.forms import CapturedLibForm
        from core.forms import BaseForm

        assert issubclass(CapturedLibForm, BaseForm)

    @patch('capturedlib.forms.SampleLib.objects')
    def test_form_meta_model(self, mock_sl_objects):
        """Test form Meta.model is CapturedLib"""
        mock_sl_objects.all.return_value = MagicMock()
        from capturedlib.forms import CapturedLibForm
        from capturedlib.models import CapturedLib

        assert CapturedLibForm.Meta.model == CapturedLib

    @patch('capturedlib.forms.SampleLib.objects')
    def test_form_meta_fields(self, mock_sl_objects):
        """Test form Meta.fields is __all__"""
        mock_sl_objects.all.return_value = MagicMock()
        from capturedlib.forms import CapturedLibForm

        assert CapturedLibForm.Meta.fields == "__all__"

    @patch('capturedlib.forms.SampleLib.objects')
    def test_form_has_sample_lib_field(self, mock_sl_objects):
        """Test form has sample_lib field"""
        mock_sl_objects.all.return_value = MagicMock()
        from capturedlib.forms import CapturedLibForm

        form = CapturedLibForm()
        assert 'sample_lib' in form.fields

    @patch('capturedlib.forms.SampleLib.objects')
    def test_sample_lib_field_is_model_multiple_choice_field(self, mock_sl_objects):
        """Test sample_lib field is ModelMultipleChoiceField"""
        mock_sl_objects.all.return_value = MagicMock()
        from capturedlib.forms import CapturedLibForm

        form = CapturedLibForm()
        assert isinstance(form.fields['sample_lib'], forms.ModelMultipleChoiceField)

    @patch('capturedlib.forms.SampleLib.objects')
    def test_nm_field_not_required(self, mock_sl_objects):
        """Test nm field is not required"""
        mock_sl_objects.all.return_value = MagicMock()
        from capturedlib.forms import CapturedLibForm

        form = CapturedLibForm()
        assert form.fields['nm'].required is False

    @patch('capturedlib.forms.SampleLib.objects')
    def test_sample_lib_field_not_required(self, mock_sl_objects):
        """Test sample_lib field is not required"""
        mock_sl_objects.all.return_value = MagicMock()
        from capturedlib.forms import CapturedLibForm

        form = CapturedLibForm()
        assert form.fields['sample_lib'].required is False


class TestSequencingLibCreationForm(BaseAPITestNoDatabase):
    """Test SequencingLibCreationForm"""

    @patch('capturedlib.forms.SequencingLib.objects')
    def test_form_initialization(self, mock_seql_objects):
        """Test SequencingLibCreationForm initializes correctly"""
        mock_seql_objects.all.return_value.order_by.return_value = MagicMock()
        from capturedlib.forms import SequencingLibCreationForm

        form = SequencingLibCreationForm()
        assert form is not None

    @patch('capturedlib.forms.SequencingLib.objects')
    def test_form_inherits_from_forms_form(self, mock_seql_objects):
        """Test SequencingLibCreationForm inherits from forms.Form"""
        mock_seql_objects.all.return_value.order_by.return_value = MagicMock()
        from capturedlib.forms import SequencingLibCreationForm

        assert issubclass(SequencingLibCreationForm, forms.Form)

    @patch('capturedlib.forms.SequencingLib.objects')
    def test_form_has_sequencing_lib_field(self, mock_seql_objects):
        """Test form has sequencing_lib field"""
        mock_seql_objects.all.return_value.order_by.return_value = MagicMock()
        from capturedlib.forms import SequencingLibCreationForm

        form = SequencingLibCreationForm()
        assert 'sequencing_lib' in form.fields

    @patch('capturedlib.forms.SequencingLib.objects')
    def test_sequencing_lib_field_is_model_choice_field(self, mock_seql_objects):
        """Test sequencing_lib field is ModelChoiceField"""
        mock_seql_objects.all.return_value.order_by.return_value = MagicMock()
        from capturedlib.forms import SequencingLibCreationForm

        form = SequencingLibCreationForm()
        assert isinstance(form.fields['sequencing_lib'], forms.ModelChoiceField)

    @patch('capturedlib.forms.SequencingLib.objects')
    def test_form_has_prefix_field(self, mock_seql_objects):
        """Test form has prefix field"""
        mock_seql_objects.all.return_value.order_by.return_value = MagicMock()
        from capturedlib.forms import SequencingLibCreationForm

        form = SequencingLibCreationForm()
        assert 'prefix' in form.fields

    @patch('capturedlib.forms.SequencingLib.objects')
    def test_prefix_field_is_char_field(self, mock_seql_objects):
        """Test prefix field is CharField"""
        mock_seql_objects.all.return_value.order_by.return_value = MagicMock()
        from capturedlib.forms import SequencingLibCreationForm

        form = SequencingLibCreationForm()
        assert isinstance(form.fields['prefix'], forms.CharField)

    @patch('capturedlib.forms.SequencingLib.objects')
    def test_form_has_date_field(self, mock_seql_objects):
        """Test form has date field"""
        mock_seql_objects.all.return_value.order_by.return_value = MagicMock()
        from capturedlib.forms import SequencingLibCreationForm

        form = SequencingLibCreationForm()
        assert 'date' in form.fields

    @patch('capturedlib.forms.SequencingLib.objects')
    def test_date_field_is_date_field(self, mock_seql_objects):
        """Test date field is DateField"""
        mock_seql_objects.all.return_value.order_by.return_value = MagicMock()
        from capturedlib.forms import SequencingLibCreationForm

        form = SequencingLibCreationForm()
        assert isinstance(form.fields['date'], forms.DateField)

    @patch('capturedlib.forms.SequencingLib.objects')
    def test_form_has_buffer_field(self, mock_seql_objects):
        """Test form has buffer field"""
        mock_seql_objects.all.return_value.order_by.return_value = MagicMock()
        from capturedlib.forms import SequencingLibCreationForm

        form = SequencingLibCreationForm()
        assert 'buffer' in form.fields

    @patch('capturedlib.forms.SequencingLib.objects')
    def test_buffer_field_is_choice_field(self, mock_seql_objects):
        """Test buffer field is ChoiceField"""
        mock_seql_objects.all.return_value.order_by.return_value = MagicMock()
        from capturedlib.forms import SequencingLibCreationForm

        form = SequencingLibCreationForm()
        assert isinstance(form.fields['buffer'], forms.ChoiceField)

    @patch('capturedlib.forms.SequencingLib.objects')
    def test_form_has_nm_field(self, mock_seql_objects):
        """Test form has nm field"""
        mock_seql_objects.all.return_value.order_by.return_value = MagicMock()
        from capturedlib.forms import SequencingLibCreationForm

        form = SequencingLibCreationForm()
        assert 'nm' in form.fields

    @patch('capturedlib.forms.SequencingLib.objects')
    def test_nm_field_is_float_field(self, mock_seql_objects):
        """Test nm field is FloatField"""
        mock_seql_objects.all.return_value.order_by.return_value = MagicMock()
        from capturedlib.forms import SequencingLibCreationForm

        form = SequencingLibCreationForm()
        assert isinstance(form.fields['nm'], forms.FloatField)

    @patch('capturedlib.forms.SequencingLib.objects')
    def test_form_has_vol_init_field(self, mock_seql_objects):
        """Test form has vol_init field"""
        mock_seql_objects.all.return_value.order_by.return_value = MagicMock()
        from capturedlib.forms import SequencingLibCreationForm

        form = SequencingLibCreationForm()
        assert 'vol_init' in form.fields

    @patch('capturedlib.forms.SequencingLib.objects')
    def test_vol_init_field_is_float_field(self, mock_seql_objects):
        """Test vol_init field is FloatField"""
        mock_seql_objects.all.return_value.order_by.return_value = MagicMock()
        from capturedlib.forms import SequencingLibCreationForm

        form = SequencingLibCreationForm()
        assert isinstance(form.fields['vol_init'], forms.FloatField)


class TestFilterForm(BaseAPITestNoDatabase):
    """Test FilterForm"""

    @patch('capturedlib.forms.Bait.objects')
    def test_form_initialization(self, mock_bait_objects):
        """Test FilterForm initializes correctly"""
        mock_bait_objects.all.return_value.order_by.return_value = MagicMock()
        from capturedlib.forms import FilterForm

        form = FilterForm()
        assert form is not None

    @patch('capturedlib.forms.Bait.objects')
    def test_form_inherits_from_forms_form(self, mock_bait_objects):
        """Test FilterForm inherits from forms.Form"""
        mock_bait_objects.all.return_value.order_by.return_value = MagicMock()
        from capturedlib.forms import FilterForm

        assert issubclass(FilterForm, forms.Form)

    @patch('capturedlib.forms.Bait.objects')
    def test_form_has_area_type_field(self, mock_bait_objects):
        """Test form has area_type field"""
        mock_bait_objects.all.return_value.order_by.return_value = MagicMock()
        from capturedlib.forms import FilterForm

        form = FilterForm()
        assert 'area_type' in form.fields

    @patch('capturedlib.forms.Bait.objects')
    def test_area_type_field_is_choice_field(self, mock_bait_objects):
        """Test area_type field is ChoiceField"""
        mock_bait_objects.all.return_value.order_by.return_value = MagicMock()
        from capturedlib.forms import FilterForm

        form = FilterForm()
        assert isinstance(form.fields['area_type'], forms.ChoiceField)

    @patch('capturedlib.forms.Bait.objects')
    def test_area_type_field_not_required(self, mock_bait_objects):
        """Test area_type field is not required"""
        mock_bait_objects.all.return_value.order_by.return_value = MagicMock()
        from capturedlib.forms import FilterForm

        form = FilterForm()
        assert form.fields['area_type'].required is False

    @patch('capturedlib.forms.Bait.objects')
    def test_form_has_bait_field(self, mock_bait_objects):
        """Test form has bait field"""
        mock_bait_objects.all.return_value.order_by.return_value = MagicMock()
        from capturedlib.forms import FilterForm

        form = FilterForm()
        assert 'bait' in form.fields

    @patch('capturedlib.forms.Bait.objects')
    def test_bait_field_is_model_choice_field(self, mock_bait_objects):
        """Test bait field is ModelChoiceField"""
        mock_bait_objects.all.return_value.order_by.return_value = MagicMock()
        from capturedlib.forms import FilterForm

        form = FilterForm()
        assert isinstance(form.fields['bait'], forms.ModelChoiceField)

    @patch('capturedlib.forms.Bait.objects')
    def test_bait_field_has_css_class(self, mock_bait_objects):
        """Test bait field has form-control-sm CSS class"""
        mock_bait_objects.all.return_value.order_by.return_value = MagicMock()
        from capturedlib.forms import FilterForm

        form = FilterForm()
        assert 'class' in form.fields['bait'].widget.attrs
        assert form.fields['bait'].widget.attrs['class'] == 'form-control-sm'


class TestFormIntegration(BaseAPITestNoDatabase):
    """Test form integration"""

    @patch('capturedlib.forms.SampleLib.objects')
    def test_capturedlib_form_instantiation(self, mock_sl_objects):
        """Test CapturedLibForm can be instantiated"""
        mock_sl_objects.all.return_value = MagicMock()
        from capturedlib.forms import CapturedLibForm

        form = CapturedLibForm()
        assert form is not None
        assert hasattr(form, 'fields')

    @patch('capturedlib.forms.SequencingLib.objects')
    def test_sequencinglib_creation_form_instantiation(self, mock_seql_objects):
        """Test SequencingLibCreationForm can be instantiated"""
        mock_seql_objects.all.return_value.order_by.return_value = MagicMock()
        from capturedlib.forms import SequencingLibCreationForm

        form = SequencingLibCreationForm()
        assert form is not None
        assert hasattr(form, 'fields')

    @patch('capturedlib.forms.Bait.objects')
    def test_filter_form_instantiation(self, mock_bait_objects):
        """Test FilterForm can be instantiated"""
        mock_bait_objects.all.return_value.order_by.return_value = MagicMock()
        from capturedlib.forms import FilterForm

        form = FilterForm()
        assert form is not None
        assert hasattr(form, 'fields')
