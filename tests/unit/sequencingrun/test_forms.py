# tests/unit/sequencingrun/test_forms.py
"""
Sequencingrun Forms Test Cases - No Database Required
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django import forms
from tests.utils.base_test import BaseAPITestNoDatabase
from tests.fixtures.sequencingrun_fixtures import SequencingrunTestData


class TestSequencingRunForm(BaseAPITestNoDatabase):
    """Test SequencingRunForm"""

    def test_form_initialization(self):
        """Test SequencingRunForm initializes correctly"""
        from sequencingrun.forms import SequencingRunForm

        form = SequencingRunForm()
        assert form is not None

    def test_form_inherits_from_base_form(self):
        """Test SequencingRunForm inherits from BaseForm"""
        from sequencingrun.forms import SequencingRunForm
        from core.forms import BaseForm

        assert issubclass(SequencingRunForm, BaseForm)

    def test_form_meta_model(self):
        """Test form Meta.model is SequencingRun"""
        from sequencingrun.forms import SequencingRunForm
        from sequencingrun.models import SequencingRun

        assert SequencingRunForm.Meta.model == SequencingRun

    def test_form_meta_fields(self):
        """Test form Meta.fields is __all__"""
        from sequencingrun.forms import SequencingRunForm

        assert SequencingRunForm.Meta.fields == "__all__"


class TestSequencingRunCreationForm(BaseAPITestNoDatabase):
    """Test SequencingRunCreationForm"""

    def test_form_initialization(self):
        """Test SequencingRunCreationForm initializes correctly"""
        from sequencingrun.forms import SequencingRunCreationForm

        form = SequencingRunCreationForm()
        assert form is not None

    def test_form_inherits_from_forms_form(self):
        """Test SequencingRunCreationForm inherits from forms.Form"""
        from sequencingrun.forms import SequencingRunCreationForm

        assert issubclass(SequencingRunCreationForm, forms.Form)

    def test_form_has_prefix_field(self):
        """Test form has prefix field"""
        from sequencingrun.forms import SequencingRunCreationForm

        form = SequencingRunCreationForm()
        assert 'prefix' in form.fields

    def test_prefix_field_is_char_field(self):
        """Test prefix field is CharField"""
        from sequencingrun.forms import SequencingRunCreationForm

        form = SequencingRunCreationForm()
        assert isinstance(form.fields['prefix'], forms.CharField)

    def test_form_has_date_run_field(self):
        """Test form has date_run field"""
        from sequencingrun.forms import SequencingRunCreationForm

        form = SequencingRunCreationForm()
        assert 'date_run' in form.fields

    def test_date_run_field_is_datetime_field(self):
        """Test date_run field is DateTimeField"""
        from sequencingrun.forms import SequencingRunCreationForm

        form = SequencingRunCreationForm()
        assert isinstance(form.fields['date_run'], forms.DateTimeField)

    def test_form_has_date_field(self):
        """Test form has date field"""
        from sequencingrun.forms import SequencingRunCreationForm

        form = SequencingRunCreationForm()
        assert 'date' in form.fields

    def test_date_field_is_date_field(self):
        """Test date field is DateField"""
        from sequencingrun.forms import SequencingRunCreationForm

        form = SequencingRunCreationForm()
        assert isinstance(form.fields['date'], forms.DateField)

    def test_form_has_facility_field(self):
        """Test form has facility field"""
        from sequencingrun.forms import SequencingRunCreationForm

        form = SequencingRunCreationForm()
        assert 'facility' in form.fields

    def test_facility_field_is_choice_field(self):
        """Test facility field is ChoiceField"""
        from sequencingrun.forms import SequencingRunCreationForm

        form = SequencingRunCreationForm()
        assert isinstance(form.fields['facility'], forms.ChoiceField)

    def test_form_has_sequencer_field(self):
        """Test form has sequencer field"""
        from sequencingrun.forms import SequencingRunCreationForm

        form = SequencingRunCreationForm()
        assert 'sequencer' in form.fields

    def test_sequencer_field_is_choice_field(self):
        """Test sequencer field is ChoiceField"""
        from sequencingrun.forms import SequencingRunCreationForm

        form = SequencingRunCreationForm()
        assert isinstance(form.fields['sequencer'], forms.ChoiceField)

    def test_form_has_pe_field(self):
        """Test form has pe field"""
        from sequencingrun.forms import SequencingRunCreationForm

        form = SequencingRunCreationForm()
        assert 'pe' in form.fields

    def test_pe_field_is_choice_field(self):
        """Test pe field is ChoiceField"""
        from sequencingrun.forms import SequencingRunCreationForm

        form = SequencingRunCreationForm()
        assert isinstance(form.fields['pe'], forms.ChoiceField)

    def test_form_has_amp_cycles_field(self):
        """Test form has amp_cycles field"""
        from sequencingrun.forms import SequencingRunCreationForm

        form = SequencingRunCreationForm()
        assert 'amp_cycles' in form.fields

    def test_amp_cycles_field_is_integer_field(self):
        """Test amp_cycles field is IntegerField"""
        from sequencingrun.forms import SequencingRunCreationForm

        form = SequencingRunCreationForm()
        assert isinstance(form.fields['amp_cycles'], forms.IntegerField)


class TestFormIntegration(BaseAPITestNoDatabase):
    """Test form integration"""

    def test_sequencingrun_form_instantiation(self):
        """Test SequencingRunForm can be instantiated"""
        from sequencingrun.forms import SequencingRunForm

        form = SequencingRunForm()
        assert form is not None
        assert hasattr(form, 'fields')

    def test_sequencingrun_creation_form_instantiation(self):
        """Test SequencingRunCreationForm can be instantiated"""
        from sequencingrun.forms import SequencingRunCreationForm

        form = SequencingRunCreationForm()
        assert form is not None
        assert hasattr(form, 'fields')
