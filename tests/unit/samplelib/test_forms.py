# tests/unit/samplelib/test_forms.py
"""
Samplelib Forms Test Cases - No Database Required
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django import forms
from tests.utils.base_test import BaseAPITestNoDatabase
from tests.fixtures.samplelib_fixtures import SamplelibTestData


class TestSampleLibForm(BaseAPITestNoDatabase):
    """Test SampleLibForm"""

    @patch('samplelib.forms.NucAcids.objects')
    @patch('samplelib.forms.CapturedLib.objects')
    def test_form_initialization(self, mock_cl_objects, mock_na_objects):
        """Test SampleLibForm initializes correctly"""
        # Setup mocks
        mock_na_objects.all.return_value = MagicMock()
        mock_cl_objects.all.return_value = MagicMock()

        from samplelib.forms import SampleLibForm
        form = SampleLibForm()

        assert form is not None

    @patch('samplelib.forms.NucAcids.objects')
    @patch('samplelib.forms.CapturedLib.objects')
    def test_form_inherits_from_base_form(self, mock_cl_objects, mock_na_objects):
        """Test SampleLibForm inherits from BaseForm"""
        from samplelib.forms import SampleLibForm
        from core.forms import BaseForm

        assert issubclass(SampleLibForm, BaseForm)

    @patch('samplelib.forms.NucAcids.objects')
    @patch('samplelib.forms.CapturedLib.objects')
    def test_form_inherits_from_model_form(self, mock_cl_objects, mock_na_objects):
        """Test SampleLibForm inherits from ModelForm"""
        from samplelib.forms import SampleLibForm

        assert issubclass(SampleLibForm, forms.ModelForm)

    @patch('samplelib.forms.NucAcids.objects')
    @patch('samplelib.forms.CapturedLib.objects')
    def test_form_meta_model(self, mock_cl_objects, mock_na_objects):
        """Test form Meta.model is SampleLib"""
        from samplelib.forms import SampleLibForm
        from samplelib.models import SampleLib

        assert SampleLibForm.Meta.model == SampleLib

    @patch('samplelib.forms.NucAcids.objects')
    @patch('samplelib.forms.CapturedLib.objects')
    def test_form_meta_fields(self, mock_cl_objects, mock_na_objects):
        """Test form Meta.fields is __all__"""
        from samplelib.forms import SampleLibForm

        assert SampleLibForm.Meta.fields == "__all__"

    @patch('samplelib.forms.NucAcids.objects')
    @patch('samplelib.forms.CapturedLib.objects')
    def test_form_has_nuc_acid_field(self, mock_cl_objects, mock_na_objects):
        """Test form has nuc_acid field"""
        # Setup mocks
        mock_na_objects.all.return_value = MagicMock()
        mock_cl_objects.all.return_value = MagicMock()

        from samplelib.forms import SampleLibForm
        form = SampleLibForm()

        assert 'nuc_acid' in form.fields

    @patch('samplelib.forms.NucAcids.objects')
    @patch('samplelib.forms.CapturedLib.objects')
    def test_nuc_acid_field_is_model_multiple_choice_field(self, mock_cl_objects, mock_na_objects):
        """Test nuc_acid field is ModelMultipleChoiceField"""
        # Setup mocks
        mock_na_objects.all.return_value = MagicMock()
        mock_cl_objects.all.return_value = MagicMock()

        from samplelib.forms import SampleLibForm
        form = SampleLibForm()

        assert isinstance(form.fields['nuc_acid'], forms.ModelMultipleChoiceField)

    @patch('samplelib.forms.NucAcids.objects')
    @patch('samplelib.forms.CapturedLib.objects')
    def test_form_has_captured_libs_field(self, mock_cl_objects, mock_na_objects):
        """Test form has captured_libs field"""
        # Setup mocks
        mock_na_objects.all.return_value = MagicMock()
        mock_cl_objects.all.return_value = MagicMock()

        from samplelib.forms import SampleLibForm
        form = SampleLibForm()

        assert 'captured_libs' in form.fields

    @patch('samplelib.forms.NucAcids.objects')
    @patch('samplelib.forms.CapturedLib.objects')
    def test_captured_libs_field_is_model_multiple_choice_field(self, mock_cl_objects, mock_na_objects):
        """Test captured_libs field is ModelMultipleChoiceField"""
        # Setup mocks
        mock_na_objects.all.return_value = MagicMock()
        mock_cl_objects.all.return_value = MagicMock()

        from samplelib.forms import SampleLibForm
        form = SampleLibForm()

        assert isinstance(form.fields['captured_libs'], forms.ModelMultipleChoiceField)

    @patch('samplelib.forms.NucAcids.objects')
    @patch('samplelib.forms.CapturedLib.objects')
    def test_nuc_acid_field_not_required(self, mock_cl_objects, mock_na_objects):
        """Test nuc_acid field is not required"""
        # Setup mocks
        mock_na_objects.all.return_value = MagicMock()
        mock_cl_objects.all.return_value = MagicMock()

        from samplelib.forms import SampleLibForm
        form = SampleLibForm()

        assert form.fields['nuc_acid'].required is False


class TestCapturedLibCreationOptionsForm(BaseAPITestNoDatabase):
    """Test CapturedLibCreationOptionsForm"""

    @patch('samplelib.forms.Bait.objects')
    def test_form_initialization(self, mock_bait_objects):
        """Test CapturedLibCreationOptionsForm initializes correctly"""
        # Setup mock
        mock_bait_objects.all.return_value = MagicMock()

        from samplelib.forms import CapturedLibCreationOptionsForm
        form = CapturedLibCreationOptionsForm()

        assert form is not None

    @patch('samplelib.forms.Bait.objects')
    def test_form_inherits_from_forms_form(self, mock_bait_objects):
        """Test CapturedLibCreationOptionsForm inherits from forms.Form"""
        from samplelib.forms import CapturedLibCreationOptionsForm

        assert issubclass(CapturedLibCreationOptionsForm, forms.Form)

    @patch('samplelib.forms.Bait.objects')
    def test_form_has_prefix_field(self, mock_bait_objects):
        """Test form has prefix field"""
        # Setup mock
        mock_bait_objects.all.return_value = MagicMock()

        from samplelib.forms import CapturedLibCreationOptionsForm
        form = CapturedLibCreationOptionsForm()

        assert 'prefix' in form.fields

    @patch('samplelib.forms.Bait.objects')
    def test_prefix_field_is_char_field(self, mock_bait_objects):
        """Test prefix field is CharField"""
        # Setup mock
        mock_bait_objects.all.return_value = MagicMock()

        from samplelib.forms import CapturedLibCreationOptionsForm
        form = CapturedLibCreationOptionsForm()

        assert isinstance(form.fields['prefix'], forms.CharField)

    @patch('samplelib.forms.Bait.objects')
    def test_form_has_date_field(self, mock_bait_objects):
        """Test form has date field"""
        # Setup mock
        mock_bait_objects.all.return_value = MagicMock()

        from samplelib.forms import CapturedLibCreationOptionsForm
        form = CapturedLibCreationOptionsForm()

        assert 'date' in form.fields

    @patch('samplelib.forms.Bait.objects')
    def test_date_field_is_date_field(self, mock_bait_objects):
        """Test date field is DateField"""
        # Setup mock
        mock_bait_objects.all.return_value = MagicMock()

        from samplelib.forms import CapturedLibCreationOptionsForm
        form = CapturedLibCreationOptionsForm()

        assert isinstance(form.fields['date'], forms.DateField)

    @patch('samplelib.forms.Bait.objects')
    def test_form_has_bait_field(self, mock_bait_objects):
        """Test form has bait field"""
        # Setup mock
        mock_bait_objects.all.return_value = MagicMock()

        from samplelib.forms import CapturedLibCreationOptionsForm
        form = CapturedLibCreationOptionsForm()

        assert 'bait' in form.fields

    @patch('samplelib.forms.Bait.objects')
    def test_bait_field_is_model_choice_field(self, mock_bait_objects):
        """Test bait field is ModelChoiceField"""
        # Setup mock
        mock_bait_objects.all.return_value = MagicMock()

        from samplelib.forms import CapturedLibCreationOptionsForm
        form = CapturedLibCreationOptionsForm()

        assert isinstance(form.fields['bait'], forms.ModelChoiceField)


class TestFilterForm(BaseAPITestNoDatabase):
    """Test FilterForm"""

    @patch('samplelib.forms.SequencingRun.objects')
    @patch('samplelib.forms.Barcode.objects')
    @patch('samplelib.forms.Bait.objects')
    def test_form_initialization(self, mock_bait_objects, mock_barcode_objects, mock_sr_objects):
        """Test FilterForm initializes correctly"""
        # Setup mocks
        mock_sr_objects.all.return_value.order_by.return_value = MagicMock()
        mock_barcode_objects.filter.return_value = MagicMock()
        mock_bait_objects.all.return_value = MagicMock()

        from samplelib.forms import FilterForm
        form = FilterForm()

        assert form is not None

    @patch('samplelib.forms.SequencingRun.objects')
    @patch('samplelib.forms.Barcode.objects')
    @patch('samplelib.forms.Bait.objects')
    def test_form_inherits_from_forms_form(self, mock_bait_objects, mock_barcode_objects, mock_sr_objects):
        """Test FilterForm inherits from forms.Form"""
        from samplelib.forms import FilterForm

        assert issubclass(FilterForm, forms.Form)

    @patch('samplelib.forms.SequencingRun.objects')
    @patch('samplelib.forms.Barcode.objects')
    @patch('samplelib.forms.Bait.objects')
    def test_form_has_sequencing_run_field(self, mock_bait_objects, mock_barcode_objects, mock_sr_objects):
        """Test form has sequencing_run field"""
        # Setup mocks
        mock_sr_objects.all.return_value.order_by.return_value = MagicMock()
        mock_barcode_objects.filter.return_value = MagicMock()
        mock_bait_objects.all.return_value = MagicMock()

        from samplelib.forms import FilterForm
        form = FilterForm()

        assert 'sequencing_run' in form.fields

    @patch('samplelib.forms.SequencingRun.objects')
    @patch('samplelib.forms.Barcode.objects')
    @patch('samplelib.forms.Bait.objects')
    def test_sequencing_run_field_is_model_choice_field(self, mock_bait_objects, mock_barcode_objects, mock_sr_objects):
        """Test sequencing_run field is ModelChoiceField"""
        # Setup mocks
        mock_sr_objects.all.return_value.order_by.return_value = MagicMock()
        mock_barcode_objects.filter.return_value = MagicMock()
        mock_bait_objects.all.return_value = MagicMock()

        from samplelib.forms import FilterForm
        form = FilterForm()

        assert isinstance(form.fields['sequencing_run'], forms.ModelChoiceField)

    @patch('samplelib.forms.SequencingRun.objects')
    @patch('samplelib.forms.Barcode.objects')
    @patch('samplelib.forms.Bait.objects')
    def test_form_has_barcode_field(self, mock_bait_objects, mock_barcode_objects, mock_sr_objects):
        """Test form has barcode field"""
        # Setup mocks
        mock_sr_objects.all.return_value.order_by.return_value = MagicMock()
        mock_barcode_objects.filter.return_value = MagicMock()
        mock_bait_objects.all.return_value = MagicMock()

        from samplelib.forms import FilterForm
        form = FilterForm()

        assert 'barcode' in form.fields

    @patch('samplelib.forms.SequencingRun.objects')
    @patch('samplelib.forms.Barcode.objects')
    @patch('samplelib.forms.Bait.objects')
    def test_form_has_i5_field(self, mock_bait_objects, mock_barcode_objects, mock_sr_objects):
        """Test form has i5 field"""
        # Setup mocks
        mock_sr_objects.all.return_value.order_by.return_value = MagicMock()
        mock_barcode_objects.filter.return_value = MagicMock()
        mock_bait_objects.all.return_value = MagicMock()

        from samplelib.forms import FilterForm
        form = FilterForm()

        assert 'i5' in form.fields

    @patch('samplelib.forms.SequencingRun.objects')
    @patch('samplelib.forms.Barcode.objects')
    @patch('samplelib.forms.Bait.objects')
    def test_i5_field_is_char_field(self, mock_bait_objects, mock_barcode_objects, mock_sr_objects):
        """Test i5 field is CharField"""
        # Setup mocks
        mock_sr_objects.all.return_value.order_by.return_value = MagicMock()
        mock_barcode_objects.filter.return_value = MagicMock()
        mock_bait_objects.all.return_value = MagicMock()

        from samplelib.forms import FilterForm
        form = FilterForm()

        assert isinstance(form.fields['i5'], forms.CharField)

    @patch('samplelib.forms.SequencingRun.objects')
    @patch('samplelib.forms.Barcode.objects')
    @patch('samplelib.forms.Bait.objects')
    def test_form_has_i7_field(self, mock_bait_objects, mock_barcode_objects, mock_sr_objects):
        """Test form has i7 field"""
        # Setup mocks
        mock_sr_objects.all.return_value.order_by.return_value = MagicMock()
        mock_barcode_objects.filter.return_value = MagicMock()
        mock_bait_objects.all.return_value = MagicMock()

        from samplelib.forms import FilterForm
        form = FilterForm()

        assert 'i7' in form.fields

    @patch('samplelib.forms.SequencingRun.objects')
    @patch('samplelib.forms.Barcode.objects')
    @patch('samplelib.forms.Bait.objects')
    def test_form_has_area_type_field(self, mock_bait_objects, mock_barcode_objects, mock_sr_objects):
        """Test form has area_type field"""
        # Setup mocks
        mock_sr_objects.all.return_value.order_by.return_value = MagicMock()
        mock_barcode_objects.filter.return_value = MagicMock()
        mock_bait_objects.all.return_value = MagicMock()

        from samplelib.forms import FilterForm
        form = FilterForm()

        assert 'area_type' in form.fields

    @patch('samplelib.forms.SequencingRun.objects')
    @patch('samplelib.forms.Barcode.objects')
    @patch('samplelib.forms.Bait.objects')
    def test_area_type_field_is_choice_field(self, mock_bait_objects, mock_barcode_objects, mock_sr_objects):
        """Test area_type field is ChoiceField"""
        # Setup mocks
        mock_sr_objects.all.return_value.order_by.return_value = MagicMock()
        mock_barcode_objects.filter.return_value = MagicMock()
        mock_bait_objects.all.return_value = MagicMock()

        from samplelib.forms import FilterForm
        form = FilterForm()

        assert isinstance(form.fields['area_type'], forms.ChoiceField)

    @patch('samplelib.forms.SequencingRun.objects')
    @patch('samplelib.forms.Barcode.objects')
    @patch('samplelib.forms.Bait.objects')
    def test_area_type_field_not_required(self, mock_bait_objects, mock_barcode_objects, mock_sr_objects):
        """Test area_type field is not required"""
        # Setup mocks
        mock_sr_objects.all.return_value.order_by.return_value = MagicMock()
        mock_barcode_objects.filter.return_value = MagicMock()
        mock_bait_objects.all.return_value = MagicMock()

        from samplelib.forms import FilterForm
        form = FilterForm()

        assert form.fields['area_type'].required is False

    @patch('samplelib.forms.SequencingRun.objects')
    @patch('samplelib.forms.Barcode.objects')
    @patch('samplelib.forms.Bait.objects')
    def test_form_has_bait_field(self, mock_bait_objects, mock_barcode_objects, mock_sr_objects):
        """Test form has bait field"""
        # Setup mocks
        mock_sr_objects.all.return_value.order_by.return_value = MagicMock()
        mock_barcode_objects.filter.return_value = MagicMock()
        mock_bait_objects.all.return_value = MagicMock()

        from samplelib.forms import FilterForm
        form = FilterForm()

        assert 'bait' in form.fields


class TestCapturedLibAddForm(BaseAPITestNoDatabase):
    """Test CapturedLibAddForm"""

    @patch('samplelib.forms.CapturedLib.objects')
    def test_form_initialization(self, mock_cl_objects):
        """Test CapturedLibAddForm initializes correctly"""
        # Setup mock
        mock_cl_objects.all.return_value.order_by.return_value = MagicMock()

        from samplelib.forms import CapturedLibAddForm
        form = CapturedLibAddForm()

        assert form is not None

    @patch('samplelib.forms.CapturedLib.objects')
    def test_form_inherits_from_forms_form(self, mock_cl_objects):
        """Test CapturedLibAddForm inherits from forms.Form"""
        from samplelib.forms import CapturedLibAddForm

        assert issubclass(CapturedLibAddForm, forms.Form)

    @patch('samplelib.forms.CapturedLib.objects')
    def test_form_has_captured_lib_field(self, mock_cl_objects):
        """Test form has captured_lib field"""
        # Setup mock
        mock_cl_objects.all.return_value.order_by.return_value = MagicMock()

        from samplelib.forms import CapturedLibAddForm
        form = CapturedLibAddForm()

        assert 'captured_lib' in form.fields

    @patch('samplelib.forms.CapturedLib.objects')
    def test_captured_lib_field_is_model_choice_field(self, mock_cl_objects):
        """Test captured_lib field is ModelChoiceField"""
        # Setup mock
        mock_cl_objects.all.return_value.order_by.return_value = MagicMock()

        from samplelib.forms import CapturedLibAddForm
        form = CapturedLibAddForm()

        assert isinstance(form.fields['captured_lib'], forms.ModelChoiceField)


class TestFormIntegration(BaseAPITestNoDatabase):
    """Integration tests for forms"""

    @patch('samplelib.forms.NucAcids.objects')
    @patch('samplelib.forms.CapturedLib.objects')
    def test_samplelib_form_instantiation(self, mock_cl_objects, mock_na_objects):
        """Test SampleLibForm can be instantiated"""
        # Setup mocks
        mock_na_objects.all.return_value = MagicMock()
        mock_cl_objects.all.return_value = MagicMock()

        from samplelib.forms import SampleLibForm

        form = SampleLibForm()
        assert form is not None

    @patch('samplelib.forms.Bait.objects')
    def test_capturedlib_options_form_instantiation(self, mock_bait_objects):
        """Test CapturedLibCreationOptionsForm can be instantiated"""
        # Setup mock
        mock_bait_objects.all.return_value = MagicMock()

        from samplelib.forms import CapturedLibCreationOptionsForm

        form = CapturedLibCreationOptionsForm()
        assert form is not None

    @patch('samplelib.forms.SequencingRun.objects')
    @patch('samplelib.forms.Barcode.objects')
    @patch('samplelib.forms.Bait.objects')
    def test_filter_form_instantiation(self, mock_bait_objects, mock_barcode_objects, mock_sr_objects):
        """Test FilterForm can be instantiated"""
        # Setup mocks
        mock_sr_objects.all.return_value.order_by.return_value = MagicMock()
        mock_barcode_objects.filter.return_value = MagicMock()
        mock_bait_objects.all.return_value = MagicMock()

        from samplelib.forms import FilterForm

        form = FilterForm()
        assert form is not None

    @patch('samplelib.forms.CapturedLib.objects')
    def test_capturedlib_add_form_instantiation(self, mock_cl_objects):
        """Test CapturedLibAddForm can be instantiated"""
        # Setup mock
        mock_cl_objects.all.return_value.order_by.return_value = MagicMock()

        from samplelib.forms import CapturedLibAddForm

        form = CapturedLibAddForm()
        assert form is not None
