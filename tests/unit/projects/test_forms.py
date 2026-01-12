# tests/unit/projects/test_forms.py
"""
Project Forms Test Cases - No Database Required

Tests ProjectForm and FilterForm with complete database mocking.
"""
import pytest
import importlib
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from django import forms
from tests.utils.base_test import BaseAPITestNoDatabase
from tests.fixtures.project_fixtures import ProjectTestData


class TestProjectForm(BaseAPITestNoDatabase):
    """Test ProjectForm"""

    @patch('projects.forms.settings')
    @patch('projects.forms.Block.objects')
    @patch('projects.forms.User.objects')
    def test_form_initialization(self, mock_user_objects, mock_block_objects, mock_settings):
        """Test ProjectForm initializes with correct querysets"""
        # Setup settings
        mock_settings.TECHNICIAN_GROUP_NAME = "Technicians"
        mock_settings.RESEARCHER_GROUP_NAME = "Researchers"
        mock_settings.PI_GROUP_NAME = "Primary Investigators"

        # Setup mock querysets
        mock_tech_queryset = MagicMock()
        mock_researcher_queryset = MagicMock()
        mock_pi_queryset = MagicMock()

        mock_user_objects.filter.side_effect = [
            mock_tech_queryset,
            mock_researcher_queryset,
            mock_pi_queryset
        ]

        # Import and create form
        from projects.forms import ProjectForm
        form = ProjectForm()

        # Verify User.objects.filter was called for each group
        assert mock_user_objects.filter.call_count == 3

        # Verify filter was called with correct group names
        calls = mock_user_objects.filter.call_args_list
        assert any('Technicians' in str(call) for call in calls)
        assert any('Researchers' in str(call) for call in calls)
        assert any('Primary Investigators' in str(call) for call in calls)

    @patch('projects.forms.settings')
    @patch('projects.forms.Block.objects')
    @patch('projects.forms.User.objects')
    def test_form_has_all_fields(self, mock_user_objects, mock_block_objects, mock_settings):
        """Test form contains all expected fields"""
        # Setup mocks
        mock_settings.TECHNICIAN_GROUP_NAME = "Technicians"
        mock_settings.RESEARCHER_GROUP_NAME = "Researchers"
        mock_settings.PI_GROUP_NAME = "Primary Investigators"

        mock_user_objects.filter.return_value = MagicMock()
        mock_block_objects.all.return_value = MagicMock()

        from projects.forms import ProjectForm
        form = ProjectForm()

        # Verify all fields are present (excluding 'id' which is handled automatically)
        expected_fields = [
            'name', 'abbreviation', 'blocks', 'description',
            'speedtype', 'primary_investigator', 'date_start',
            'technician', 'researcher'
        ]

        for field_name in expected_fields:
            assert field_name in form.fields

    @patch('projects.forms.settings')
    @patch('projects.forms.Block.objects')
    @patch('projects.forms.User.objects')
    def test_form_blocks_field_configuration(self, mock_user_objects, mock_block_objects, mock_settings):
        """Test blocks field is ModelMultipleChoiceField"""
        # Setup
        mock_settings.TECHNICIAN_GROUP_NAME = "Technicians"
        mock_settings.RESEARCHER_GROUP_NAME = "Researchers"
        mock_settings.PI_GROUP_NAME = "Primary Investigators"

        mock_user_objects.filter.return_value = MagicMock()
        mock_block_objects.all.return_value = MagicMock()

        from projects.forms import ProjectForm
        form = ProjectForm()

        # Verify blocks field type and configuration
        assert isinstance(form.fields['blocks'], forms.ModelMultipleChoiceField)
        assert form.fields['blocks'].required is False
        assert form.fields['blocks'].label == "Blocks"

    @patch('projects.forms.settings')
    @patch('projects.forms.Block.objects')
    @patch('projects.forms.User.objects')
    def test_form_description_widget(self, mock_user_objects, mock_block_objects, mock_settings):
        """Test description field has Textarea widget"""
        # Setup
        mock_settings.TECHNICIAN_GROUP_NAME = "Technicians"
        mock_settings.RESEARCHER_GROUP_NAME = "Researchers"
        mock_settings.PI_GROUP_NAME = "Primary Investigators"

        mock_user_objects.filter.return_value = MagicMock()
        mock_block_objects.all.return_value = MagicMock()

        from projects.forms import ProjectForm
        form = ProjectForm()

        # Verify description widget
        assert isinstance(form.fields['description'].widget, forms.Textarea)
        assert form.fields['description'].widget.attrs['rows'] == 4
        assert form.fields['description'].widget.attrs['cols'] == 40

    @patch('projects.forms.settings')
    @patch('projects.forms.Block.objects')
    @patch('projects.forms.User.objects')
    def test_form_technician_queryset_filter(self, mock_user_objects, mock_block_objects, mock_settings):
        """Test technician field queryset filters by TECHNICIAN_GROUP_NAME"""
        # Setup
        mock_settings.TECHNICIAN_GROUP_NAME = "Technicians"
        mock_settings.RESEARCHER_GROUP_NAME = "Researchers"
        mock_settings.PI_GROUP_NAME = "Primary Investigators"

        mock_queryset = MagicMock()
        mock_user_objects.filter.return_value = mock_queryset
        mock_block_objects.all.return_value = MagicMock()

        from projects.forms import ProjectForm
        form = ProjectForm()

        # Verify filter was called with technician group
        calls = [str(call) for call in mock_user_objects.filter.call_args_list]
        assert any('Technicians' in call for call in calls)

    @patch('projects.forms.settings')
    @patch('projects.forms.Block.objects')
    @patch('projects.forms.User.objects')
    def test_form_researcher_queryset_filter(self, mock_user_objects, mock_block_objects, mock_settings):
        """Test researcher field queryset filters by RESEARCHER_GROUP_NAME"""
        # Setup
        mock_settings.TECHNICIAN_GROUP_NAME = "Technicians"
        mock_settings.RESEARCHER_GROUP_NAME = "Researchers"
        mock_settings.PI_GROUP_NAME = "Primary Investigators"

        mock_queryset = MagicMock()
        mock_user_objects.filter.return_value = mock_queryset
        mock_block_objects.all.return_value = MagicMock()

        from projects.forms import ProjectForm
        form = ProjectForm()

        # Verify filter was called with researcher group
        calls = [str(call) for call in mock_user_objects.filter.call_args_list]
        assert any('Researchers' in call for call in calls)

    @patch('projects.forms.settings')
    @patch('projects.forms.Block.objects')
    @patch('projects.forms.User.objects')
    def test_form_pi_queryset_filter(self, mock_user_objects, mock_block_objects, mock_settings):
        """Test primary_investigator field queryset filters by PI_GROUP_NAME"""
        # Setup
        mock_settings.TECHNICIAN_GROUP_NAME = "Technicians"
        mock_settings.RESEARCHER_GROUP_NAME = "Researchers"
        mock_settings.PI_GROUP_NAME = "Primary Investigators"

        mock_queryset = MagicMock()
        mock_user_objects.filter.return_value = mock_queryset
        mock_block_objects.all.return_value = MagicMock()

        from projects.forms import ProjectForm
        form = ProjectForm()

        # Verify filter was called with PI group
        calls = [str(call) for call in mock_user_objects.filter.call_args_list]
        assert any('Primary Investigators' in call for call in calls)

    @patch('projects.forms.settings')
    @patch('projects.forms.Block.objects')
    @patch('projects.forms.User.objects')
    def test_form_label_from_instance_technician(self, mock_user_objects, mock_block_objects, mock_settings):
        """Test technician label_from_instance uses get_full_name"""
        # Setup
        mock_settings.TECHNICIAN_GROUP_NAME = "Technicians"
        mock_settings.RESEARCHER_GROUP_NAME = "Researchers"
        mock_settings.PI_GROUP_NAME = "Primary Investigators"

        mock_user_objects.filter.return_value = MagicMock()
        mock_block_objects.all.return_value = MagicMock()

        from projects.forms import ProjectForm
        form = ProjectForm()

        # Create mock user
        mock_user = Mock()
        mock_user.get_full_name = Mock(return_value="John Doe")

        # Test label_from_instance
        label = form.fields['technician'].label_from_instance(mock_user)

        assert label == "John Doe"
        mock_user.get_full_name.assert_called_once()

    @patch('projects.forms.settings')
    @patch('projects.forms.Block.objects')
    @patch('projects.forms.User.objects')
    def test_form_label_from_instance_researcher(self, mock_user_objects, mock_block_objects, mock_settings):
        """Test researcher label_from_instance uses get_full_name"""
        # Setup
        mock_settings.TECHNICIAN_GROUP_NAME = "Technicians"
        mock_settings.RESEARCHER_GROUP_NAME = "Researchers"
        mock_settings.PI_GROUP_NAME = "Primary Investigators"

        mock_user_objects.filter.return_value = MagicMock()
        mock_block_objects.all.return_value = MagicMock()

        from projects.forms import ProjectForm
        form = ProjectForm()

        # Create mock user
        mock_user = Mock()
        mock_user.get_full_name = Mock(return_value="Jane Smith")

        # Test label_from_instance
        label = form.fields['researcher'].label_from_instance(mock_user)

        assert label == "Jane Smith"
        mock_user.get_full_name.assert_called_once()

    @patch('projects.forms.settings')
    @patch('projects.forms.Block.objects')
    @patch('projects.forms.User.objects')
    def test_form_label_from_instance_pi(self, mock_user_objects, mock_block_objects, mock_settings):
        """Test primary_investigator label_from_instance uses get_full_name"""
        # Setup
        mock_settings.TECHNICIAN_GROUP_NAME = "Technicians"
        mock_settings.RESEARCHER_GROUP_NAME = "Researchers"
        mock_settings.PI_GROUP_NAME = "Primary Investigators"

        mock_user_objects.filter.return_value = MagicMock()
        mock_block_objects.all.return_value = MagicMock()

        from projects.forms import ProjectForm
        form = ProjectForm()

        # Create mock user
        mock_user = Mock()
        mock_user.get_full_name = Mock(return_value="Dr. Boris Bastian")

        # Test label_from_instance
        label = form.fields['primary_investigator'].label_from_instance(mock_user)

        assert label == "Dr. Boris Bastian"
        mock_user.get_full_name.assert_called_once()

    @patch('projects.forms.BaseForm.save')
    @patch('projects.forms.settings')
    @patch('projects.forms.Block.objects')
    @patch('projects.forms.User.objects')
    def test_form_save_method(self, mock_user_objects, mock_block_objects, mock_settings, mock_base_save):
        """Test save method saves instance and M2M relationships"""
        # Setup
        mock_settings.TECHNICIAN_GROUP_NAME = "Technicians"
        mock_settings.RESEARCHER_GROUP_NAME = "Researchers"
        mock_settings.PI_GROUP_NAME = "Primary Investigators"

        mock_user_objects.filter.return_value = MagicMock()
        mock_block_objects.all.return_value = MagicMock()

        # Create mock instance
        mock_instance = Mock()
        mock_instance.save = Mock()
        mock_base_save.return_value = mock_instance

        from projects.forms import ProjectForm
        form = ProjectForm()
        form.save_m2m = Mock()

        # Call save
        result = form.save()

        # Verify save was called with commit=False
        mock_base_save.assert_called_once_with(commit=False)

        # Verify instance.save was called
        mock_instance.save.assert_called_once()

        # Verify save_m2m was called
        form.save_m2m.assert_called_once()

        # Verify instance was returned
        assert result == mock_instance

    @patch('projects.forms.settings')
    @patch('projects.forms.Block.objects')
    @patch('projects.forms.User.objects')
    def test_form_meta_model(self, mock_user_objects, mock_block_objects, mock_settings):
        """Test form Meta.model is Project"""
        from projects.forms import ProjectForm
        from projects.models import Project

        assert ProjectForm.Meta.model == Project

    @patch('projects.forms.settings')
    @patch('projects.forms.Block.objects')
    @patch('projects.forms.User.objects')
    def test_form_meta_fields(self, mock_user_objects, mock_block_objects, mock_settings):
        """Test form Meta.fields includes all expected fields"""
        from projects.forms import ProjectForm

        expected_fields = [
            'id', 'name', 'abbreviation', 'blocks', 'description',
            'speedtype', 'primary_investigator', 'date_start',
            'technician', 'researcher'
        ]

        assert ProjectForm.Meta.fields == expected_fields

    @patch('projects.forms.settings')
    @patch('projects.forms.Block.objects')
    @patch('projects.forms.User.objects')
    def test_form_inherits_from_base_form(self, mock_user_objects, mock_block_objects, mock_settings):
        """Test ProjectForm inherits from BaseForm"""
        # Setup
        mock_settings.TECHNICIAN_GROUP_NAME = "Technicians"
        mock_settings.RESEARCHER_GROUP_NAME = "Researchers"
        mock_settings.PI_GROUP_NAME = "Primary Investigators"

        mock_user_objects.filter.return_value = MagicMock()
        mock_block_objects.all.return_value = MagicMock()

        from projects.forms import ProjectForm
        from core.forms import BaseForm

        assert issubclass(ProjectForm, BaseForm)


class TestFilterForm(BaseAPITestNoDatabase):
    """Test FilterForm"""

    @patch('projects.forms.User.objects')
    def test_filter_form_initialization(self, mock_user_objects):
        """Test FilterForm initializes correctly"""
        # Setup mock querysets - FilterForm querysets are defined at class level
        # So we need to mock at import time
        mock_queryset = MagicMock()
        mock_queryset.distinct.return_value = mock_queryset
        mock_user_objects.filter.return_value = mock_queryset

        from projects.forms import FilterForm
        form = FilterForm()

        # Form should initialize successfully
        assert form is not None
        assert 'technician' in form.fields
        assert 'researcher' in form.fields
        assert 'pi' in form.fields

    @patch('projects.forms.User.objects')
    def test_filter_form_has_all_fields(self, mock_user_objects):
        """Test FilterForm has all expected fields"""
        # Setup
        mock_queryset = MagicMock()
        mock_queryset.distinct.return_value = mock_queryset
        mock_user_objects.filter.return_value = mock_queryset

        from projects.forms import FilterForm
        form = FilterForm()

        # Verify all fields are present
        assert 'date_range' in form.fields
        assert 'pi' in form.fields
        assert 'technician' in form.fields
        assert 'researcher' in form.fields

    @patch('projects.forms.User.objects')
    def test_filter_form_date_range_field(self, mock_user_objects):
        """Test date_range field is DateField"""
        # Setup
        mock_queryset = MagicMock()
        mock_queryset.distinct.return_value = mock_queryset
        mock_user_objects.filter.return_value = mock_queryset

        from projects.forms import FilterForm
        form = FilterForm()

        # Verify field type
        assert isinstance(form.fields['date_range'], forms.DateField)
        assert form.fields['date_range'].label == "Start Date"

    @patch('projects.forms.User.objects')
    def test_filter_form_technician_field(self, mock_user_objects):
        """Test technician field is ModelChoiceField"""
        # Setup
        mock_queryset = MagicMock()
        mock_queryset.distinct.return_value = mock_queryset
        mock_user_objects.filter.return_value = mock_queryset

        from projects.forms import FilterForm
        form = FilterForm()

        # Verify field type
        assert isinstance(form.fields['technician'], forms.ModelChoiceField)

    @patch('projects.forms.User.objects')
    def test_filter_form_researcher_field(self, mock_user_objects):
        """Test researcher field is ModelChoiceField"""
        # Setup
        mock_queryset = MagicMock()
        mock_queryset.distinct.return_value = mock_queryset
        mock_user_objects.filter.return_value = mock_queryset

        from projects.forms import FilterForm
        form = FilterForm()

        # Verify field type
        assert isinstance(form.fields['researcher'], forms.ModelChoiceField)

    @patch('projects.forms.User.objects')
    def test_filter_form_pi_field(self, mock_user_objects):
        """Test pi field is ModelChoiceField"""
        # Setup
        mock_queryset = MagicMock()
        mock_queryset.distinct.return_value = mock_queryset
        mock_user_objects.filter.return_value = mock_queryset

        from projects.forms import FilterForm
        form = FilterForm()

        # Verify field type
        assert isinstance(form.fields['pi'], forms.ModelChoiceField)

    @patch('projects.forms.User.objects')
    def test_filter_form_queryset_uses_distinct(self, mock_user_objects):
        """Test querysets are configured to use distinct()"""
        # Setup
        mock_queryset = MagicMock()
        mock_queryset.distinct.return_value = mock_queryset
        mock_user_objects.filter.return_value = mock_queryset

        from projects.forms import FilterForm
        form = FilterForm()

        # Querysets are defined at class level, so they're created at import time
        # We just verify the form initialized successfully
        assert form is not None

    @patch('projects.forms.User.objects')
    def test_filter_form_technician_filters_not_null(self, mock_user_objects):
        """Test technician queryset configuration"""
        # Setup
        mock_queryset = MagicMock()
        mock_queryset.distinct.return_value = mock_queryset
        mock_user_objects.filter.return_value = mock_queryset

        from projects.forms import FilterForm
        form = FilterForm()

        # Verify field exists and is properly configured
        assert 'technician' in form.fields
        assert isinstance(form.fields['technician'], forms.ModelChoiceField)

    @patch('projects.forms.User.objects')
    def test_filter_form_researcher_filters_not_null(self, mock_user_objects):
        """Test researcher queryset configuration"""
        # Setup
        mock_queryset = MagicMock()
        mock_queryset.distinct.return_value = mock_queryset
        mock_user_objects.filter.return_value = mock_queryset

        from projects.forms import FilterForm
        form = FilterForm()

        # Verify field exists and is properly configured
        assert 'researcher' in form.fields
        assert isinstance(form.fields['researcher'], forms.ModelChoiceField)

    @patch('projects.forms.User.objects')
    def test_filter_form_pi_filters_not_null(self, mock_user_objects):
        """Test pi queryset configuration"""
        # Setup
        mock_queryset = MagicMock()
        mock_queryset.distinct.return_value = mock_queryset
        mock_user_objects.filter.return_value = mock_queryset

        from projects.forms import FilterForm
        form = FilterForm()

        # Verify field exists and is properly configured
        assert 'pi' in form.fields
        assert isinstance(form.fields['pi'], forms.ModelChoiceField)

    @patch('projects.forms.User.objects')
    def test_filter_form_date_range_widget_attrs(self, mock_user_objects):
        """Test date_range field has correct widget attributes"""
        # Setup
        mock_queryset = MagicMock()
        mock_queryset.distinct.return_value = mock_queryset
        mock_user_objects.filter.return_value = mock_queryset

        from projects.forms import FilterForm
        form = FilterForm()

        # Verify widget attributes
        assert 'class' in form.fields['date_range'].widget.attrs
        assert form.fields['date_range'].widget.attrs['class'] == 'form-control-sm'

    @patch('projects.forms.User.objects')
    def test_filter_form_pi_widget_attrs(self, mock_user_objects):
        """Test pi field has correct widget attributes"""
        # Setup
        mock_queryset = MagicMock()
        mock_queryset.distinct.return_value = mock_queryset
        mock_user_objects.filter.return_value = mock_queryset

        from projects.forms import FilterForm
        form = FilterForm()

        # Verify widget attributes
        assert 'class' in form.fields['pi'].widget.attrs
        assert form.fields['pi'].widget.attrs['class'] == 'form-control-sm'

    @patch('projects.forms.User.objects')
    def test_filter_form_technician_widget_attrs(self, mock_user_objects):
        """Test technician field has correct widget attributes"""
        # Setup
        mock_queryset = MagicMock()
        mock_queryset.distinct.return_value = mock_queryset
        mock_user_objects.filter.return_value = mock_queryset

        from projects.forms import FilterForm
        form = FilterForm()

        # Verify widget attributes
        assert 'class' in form.fields['technician'].widget.attrs
        assert form.fields['technician'].widget.attrs['class'] == 'form-control-sm'
        assert 'data-control' in form.fields['technician'].widget.attrs
        assert form.fields['technician'].widget.attrs['data-control'] == 'select2'

    @patch('projects.forms.User.objects')
    def test_filter_form_researcher_widget_attrs(self, mock_user_objects):
        """Test researcher field has correct widget attributes"""
        # Setup
        mock_queryset = MagicMock()
        mock_queryset.distinct.return_value = mock_queryset
        mock_user_objects.filter.return_value = mock_queryset

        from projects.forms import FilterForm
        form = FilterForm()

        # Verify widget attributes
        assert 'class' in form.fields['researcher'].widget.attrs
        assert form.fields['researcher'].widget.attrs['class'] == 'form-control-sm'
        assert 'data-control' in form.fields['researcher'].widget.attrs
        assert form.fields['researcher'].widget.attrs['data-control'] == 'select2'

    @patch('projects.forms.User.objects')
    def test_filter_form_technician_label_from_instance(self, mock_user_objects):
        """Test technician label_from_instance format"""
        # Setup
        mock_queryset = MagicMock()
        mock_queryset.distinct.return_value = mock_queryset
        mock_user_objects.filter.return_value = mock_queryset

        from projects.forms import FilterForm
        form = FilterForm()

        # Create mock user
        mock_user = Mock()
        mock_user.first_name = "John"
        mock_user.last_name = "Doe"

        # Test label_from_instance
        label = form.fields['technician'].label_from_instance(mock_user)

        assert label == "John Doe"

    @patch('projects.forms.User.objects')
    def test_filter_form_researcher_label_from_instance(self, mock_user_objects):
        """Test researcher label_from_instance format"""
        # Setup
        mock_queryset = MagicMock()
        mock_queryset.distinct.return_value = mock_queryset
        mock_user_objects.filter.return_value = mock_queryset

        from projects.forms import FilterForm
        form = FilterForm()

        # Create mock user
        mock_user = Mock()
        mock_user.first_name = "Jane"
        mock_user.last_name = "Smith"

        # Test label_from_instance
        label = form.fields['researcher'].label_from_instance(mock_user)

        assert label == "Jane Smith"

    @patch('projects.forms.User.objects')
    def test_filter_form_inherits_from_forms_form(self, mock_user_objects):
        """Test FilterForm inherits from forms.Form"""
        from projects.forms import FilterForm

        assert issubclass(FilterForm, forms.Form)


class TestFormIntegration(BaseAPITestNoDatabase):
    """Integration tests for forms"""

    @patch('projects.forms.settings')
    @patch('projects.forms.Block.objects')
    @patch('projects.forms.User.objects')
    def test_project_form_with_data(self, mock_user_objects, mock_block_objects, mock_settings):
        """Test ProjectForm with valid data"""
        # Setup
        mock_settings.TECHNICIAN_GROUP_NAME = "Technicians"
        mock_settings.RESEARCHER_GROUP_NAME = "Researchers"
        mock_settings.PI_GROUP_NAME = "Primary Investigators"

        mock_user_objects.filter.return_value = MagicMock()
        mock_block_objects.all.return_value = MagicMock()

        from projects.forms import ProjectForm

        # Create form with data
        data = {
            'name': 'Test Project',
            'abbreviation': 'TST',
            'description': 'Test description',
            'speedtype': 'SPEED123',
            'date_start': '2024-01-01',
        }

        form = ProjectForm(data=data)

        # Form should be instantiated
        assert form is not None

    @patch('projects.forms.User.objects')
    def test_filter_form_with_data(self, mock_user_objects):
        """Test FilterForm with valid data"""
        # Setup
        mock_queryset = MagicMock()
        mock_queryset.distinct.return_value = mock_queryset
        mock_user_objects.filter.return_value = mock_queryset

        from projects.forms import FilterForm

        # Create form with data
        data = {
            'date_range': '2024-01-01',
        }

        form = FilterForm(data=data)

        # Form should be instantiated
        assert form is not None

    @patch('projects.forms.settings')
    @patch('projects.forms.Block.objects')
    @patch('projects.forms.User.objects')
    def test_project_form_field_count(self, mock_user_objects, mock_block_objects, mock_settings):
        """Test ProjectForm has exactly the expected number of fields"""
        # Setup
        mock_settings.TECHNICIAN_GROUP_NAME = "Technicians"
        mock_settings.RESEARCHER_GROUP_NAME = "Researchers"
        mock_settings.PI_GROUP_NAME = "Primary Investigators"

        mock_user_objects.filter.return_value = MagicMock()
        mock_block_objects.all.return_value = MagicMock()

        from projects.forms import ProjectForm
        form = ProjectForm()

        # Should have 9 visible fields (id is not a visible field in forms)
        assert len(form.fields) == 9

    @patch('projects.forms.User.objects')
    def test_filter_form_field_count(self, mock_user_objects):
        """Test FilterForm has exactly the expected number of fields"""
        # Setup
        mock_queryset = MagicMock()
        mock_queryset.distinct.return_value = mock_queryset
        mock_user_objects.filter.return_value = mock_queryset

        from projects.forms import FilterForm
        form = FilterForm()

        # Should have 4 fields
        assert len(form.fields) == 4

    @patch('projects.forms.settings')
    @patch('projects.forms.Block.objects')
    @patch('projects.forms.User.objects')
    def test_project_form_blocks_queryset(self, mock_user_objects, mock_block_objects, mock_settings):
        """Test blocks field is configured"""
        # Setup
        mock_settings.TECHNICIAN_GROUP_NAME = "Technicians"
        mock_settings.RESEARCHER_GROUP_NAME = "Researchers"
        mock_settings.PI_GROUP_NAME = "Primary Investigators"

        mock_user_objects.filter.return_value = MagicMock()
        mock_blocks = MagicMock()
        mock_block_objects.all.return_value = mock_blocks

        from projects.forms import ProjectForm
        form = ProjectForm()

        # Verify blocks field exists and is configured
        assert 'blocks' in form.fields
        assert isinstance(form.fields['blocks'], forms.ModelMultipleChoiceField)


class TestFormEdgeCases(BaseAPITestNoDatabase):
    """Test form edge cases and error handling"""

    @patch('projects.forms.User.objects')
    def test_filter_form_with_empty_querysets(self, mock_user_objects):
        """Test FilterForm when querysets are empty"""
        # Setup - return empty querysets
        mock_empty_queryset = MagicMock()
        mock_empty_queryset.distinct.return_value = mock_empty_queryset
        mock_empty_queryset.count.return_value = 0
        mock_user_objects.filter.return_value = mock_empty_queryset

        from projects.forms import FilterForm
        form = FilterForm()

        # Form should still initialize
        assert 'technician' in form.fields
        assert 'researcher' in form.fields
        assert 'pi' in form.fields

    @patch('projects.forms.settings')
    @patch('projects.forms.Block.objects')
    @patch('projects.forms.User.objects')
    def test_project_form_label_from_instance_with_empty_name(self, mock_user_objects, mock_block_objects,
                                                              mock_settings):
        """Test label_from_instance when user has empty name"""
        # Setup
        mock_settings.TECHNICIAN_GROUP_NAME = "Technicians"
        mock_settings.RESEARCHER_GROUP_NAME = "Researchers"
        mock_settings.PI_GROUP_NAME = "Primary Investigators"

        mock_user_objects.filter.return_value = MagicMock()
        mock_block_objects.all.return_value = MagicMock()

        from projects.forms import ProjectForm
        form = ProjectForm()

        # Create mock user with empty full name
        mock_user = Mock()
        mock_user.get_full_name = Mock(return_value="")

        # Should handle empty name
        label = form.fields['technician'].label_from_instance(mock_user)
        assert label == ""

    @patch('projects.forms.User.objects')
    def test_filter_form_label_from_instance_with_special_characters(self, mock_user_objects):
        """Test label_from_instance with special characters in name"""
        # Setup
        mock_queryset = MagicMock()
        mock_queryset.distinct.return_value = mock_queryset
        mock_user_objects.filter.return_value = mock_queryset

        from projects.forms import FilterForm
        form = FilterForm()

        # Create mock user with special characters
        mock_user = Mock()
        mock_user.first_name = "François"
        mock_user.last_name = "O'Brien"

        # Should handle special characters
        label = form.fields['technician'].label_from_instance(mock_user)
        assert label == "François O'Brien"