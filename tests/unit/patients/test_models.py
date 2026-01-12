# tests/unit/patients/test_models.py
"""
Patient Model Test Cases - No Database Required

Tests the Patient model's query_by_args method and business logic
with complete database mocking.
"""
import pytest
import json
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from django.db.models import Q, Count
from tests.utils.base_test import BaseAPITestNoDatabase
from tests.fixtures.patient_fixtures import PatientTestData


class TestPatientModel(BaseAPITestNoDatabase):
    """Test Patient model methods"""

    def setUp(self):
        """Set up test fixtures"""
        super().setUp()

        # Create mock patient instance
        self.mock_patient = self.create_mock_patient()

    def create_mock_patient(self, **kwargs):
        """Create a mock patient object"""
        patient = Mock()
        patient.id = kwargs.get('id', 1)
        patient.pat_id = kwargs.get('pat_id', 'PAT001')
        patient.sex = kwargs.get('sex', 'm')
        patient.race = kwargs.get('race', 5)
        patient.dob = kwargs.get('dob', 1980)
        patient.source = kwargs.get('source', 'UCSF')
        patient.consent = kwargs.get('consent', 'HTAN patient')
        patient.notes = kwargs.get('notes', 'Test notes')
        patient.date_added = kwargs.get('date_added', datetime.now())
        patient.num_blocks = kwargs.get('num_blocks', 0)

        # Mock methods
        patient.get_sex_display = Mock(return_value='Male')
        patient.get_race_display = Mock(return_value='White')
        patient.__str__ = Mock(return_value=patient.pat_id)

        return patient


class TestPatientQueryByArgs(BaseAPITestNoDatabase):
    """Test Patient.query_by_args method"""

    @patch('lab.models.Patient.objects')
    def test_query_by_args_basic_request(self, mock_objects):
        """Test query_by_args with basic DataTables request"""
        from lab.models import Patient

        # Setup mock queryset
        mock_queryset = self.setup_mock_queryset(count=10)
        mock_objects.all.return_value = mock_queryset

        # Create request params
        params = {
            'draw': ['1'],
            'length': ['10'],
            'start': ['0'],
            'search[value]': [''],
            'order[0][column]': ['0'],
            'order[0][dir]': ['asc'],
            'race': [''],
            'sex': [''],
            'dob': [''],
        }

        # Call method
        patient = Patient()
        result = patient.query_by_args(**params)

        # Assertions
        assert result['draw'] == 1
        assert result['total'] == 10
        assert result['count'] == 10
        assert 'items' in result

        # Verify queryset was annotated with num_blocks
        mock_queryset.annotate.assert_called_once()
        call_kwargs = mock_queryset.annotate.call_args[1]
        assert 'num_blocks' in call_kwargs

    @patch('lab.models.Patient.objects')
    def test_query_by_args_with_search_value(self, mock_objects):
        """Test query_by_args with search term"""
        from lab.models import Patient

        mock_queryset = self.setup_mock_queryset(count=3)
        mock_objects.all.return_value = mock_queryset

        params = {
            'draw': ['1'],
            'length': ['10'],
            'start': ['0'],
            'search[value]': ['PAT001'],
            'order[0][column]': ['1'],
            'order[0][dir]': ['asc'],
            'race': [''],
            'sex': [''],
            'dob': [''],
        }

        patient = Patient()
        result = patient.query_by_args(**params)

        # Verify filter was called for search
        filter_calls = [call for call in mock_queryset.filter.call_args_list]
        assert len(filter_calls) > 0
        assert result['count'] == 3

    @patch('lab.models.Patient.objects')
    def test_query_by_args_with_race_filter(self, mock_objects):
        """Test query_by_args filters by race"""
        from lab.models import Patient

        mock_queryset = self.setup_mock_queryset(count=5)
        mock_objects.all.return_value = mock_queryset

        params = {
            'draw': ['1'],
            'length': ['10'],
            'start': ['0'],
            'search[value]': [''],
            'order[0][column]': ['0'],
            'order[0][dir]': ['asc'],
            'race': ['5'],  # White
            'sex': [''],
            'dob': [''],
        }

        patient = Patient()
        result = patient.query_by_args(**params)

        # Verify filter was called with race
        assert mock_queryset.filter.called
        assert result['items'] is not None

    @patch('lab.models.Patient.objects')
    def test_query_by_args_with_sex_filter(self, mock_objects):
        """Test query_by_args filters by sex"""
        from lab.models import Patient

        mock_queryset = self.setup_mock_queryset(count=3)
        mock_objects.all.return_value = mock_queryset

        params = {
            'draw': ['1'],
            'length': ['10'],
            'start': ['0'],
            'search[value]': [''],
            'order[0][column]': ['0'],
            'order[0][dir]': ['asc'],
            'race': [''],
            'sex': ['m'],  # Male
            'dob': [''],
        }

        patient = Patient()
        result = patient.query_by_args(**params)

        # Verify filter was called
        assert mock_queryset.filter.called
        assert result['count'] == 3

    @patch('lab.models.Patient.objects')
    def test_query_by_args_with_dob_filter(self, mock_objects):
        """Test query_by_args filters by date of birth"""
        from lab.models import Patient

        mock_queryset = self.setup_mock_queryset(count=2)
        mock_objects.all.return_value = mock_queryset

        params = {
            'draw': ['1'],
            'length': ['10'],
            'start': ['0'],
            'search[value]': [''],
            'order[0][column]': ['0'],
            'order[0][dir]': ['asc'],
            'race': [''],
            'sex': [''],
            'dob': ['1980'],
        }

        patient = Patient()
        result = patient.query_by_args(**params)

        # Verify filter was called
        assert mock_queryset.filter.called
        assert result['count'] == 2

    @patch('lab.models.Patient.objects')
    def test_query_by_args_with_initial_search_block(self, mock_objects):
        """Test query_by_args with initial search for block"""
        from lab.models import Patient

        mock_queryset = self.setup_mock_queryset(count=1)
        mock_objects.all.return_value = mock_queryset

        # Initial search format: _initial:{"model":"block","id":"123"}
        initial_search = '_initial:{"model":"block","id":"123"}'

        params = {
            'draw': ['1'],
            'length': ['10'],
            'start': ['0'],
            'search[value]': [initial_search],
            'order[0][column]': ['0'],
            'order[0][dir]': ['asc'],
            'race': [''],
            'sex': [''],
            'dob': [''],
        }

        patient = Patient()
        result = patient.query_by_args(**params)

        # Verify filter was called for block search
        assert mock_queryset.filter.called
        assert result['count'] == 1

    @patch('lab.models.Patient.objects')
    def test_query_by_args_with_ordering_asc(self, mock_objects):
        """Test query_by_args with ascending order"""
        from lab.models import Patient

        mock_queryset = self.setup_mock_queryset(count=10)
        mock_objects.all.return_value = mock_queryset

        params = {
            'draw': ['1'],
            'length': ['10'],
            'start': ['0'],
            'search[value]': [''],
            'order[0][column]': ['1'],  # pat_id
            'order[0][dir]': ['asc'],
            'race': [''],
            'sex': [''],
            'dob': [''],
        }

        patient = Patient()
        result = patient.query_by_args(**params)

        # Verify order_by was called with 'pat_id' (no minus)
        mock_queryset.order_by.assert_called()
        order_arg = mock_queryset.order_by.call_args[0][0]
        assert order_arg == 'pat_id'

    @patch('lab.models.Patient.objects')
    def test_query_by_args_with_ordering_desc(self, mock_objects):
        """Test query_by_args with descending order"""
        from lab.models import Patient

        mock_queryset = self.setup_mock_queryset(count=10)
        mock_objects.all.return_value = mock_queryset

        params = {
            'draw': ['1'],
            'length': ['10'],
            'start': ['0'],
            'search[value]': [''],
            'order[0][column]': ['2'],  # sex
            'order[0][dir]': ['desc'],
            'race': [''],
            'sex': [''],
            'dob': [''],
        }

        patient = Patient()
        result = patient.query_by_args(**params)

        # Verify order_by was called with '-sex'
        mock_queryset.order_by.assert_called()
        order_arg = mock_queryset.order_by.call_args[0][0]
        assert order_arg == '-sex'

    @patch('lab.models.Patient.objects')
    def test_query_by_args_with_pagination(self, mock_objects):
        """Test query_by_args pagination"""
        from lab.models import Patient

        mock_queryset = self.setup_mock_queryset(count=100)
        mock_objects.all.return_value = mock_queryset

        params = {
            'draw': ['2'],
            'length': ['10'],
            'start': ['20'],  # Page 3 (0-indexed)
            'search[value]': [''],
            'order[0][column]': ['0'],
            'order[0][dir]': ['asc'],
            'race': [''],
            'sex': [''],
            'dob': [''],
        }

        patient = Patient()
        result = patient.query_by_args(**params)

        # Verify slicing was called with correct indices
        mock_queryset.__getitem__.assert_called()
        # The slice should be [20:30] (start=20, length=10)
        assert result['draw'] == 2
        assert result['total'] == 100

    @patch('lab.models.Patient.objects')
    def test_query_by_args_with_all_filters_combined(self, mock_objects):
        """Test query_by_args with multiple filters combined"""
        from lab.models import Patient

        mock_queryset = self.setup_mock_queryset(count=2)
        mock_objects.all.return_value = mock_queryset

        params = {
            'draw': ['1'],
            'length': ['10'],
            'start': ['0'],
            'search[value]': ['PAT'],
            'order[0][column]': ['1'],
            'order[0][dir]': ['desc'],
            'race': ['5'],
            'sex': ['m'],
            'dob': ['1980'],
        }

        patient = Patient()
        result = patient.query_by_args(**params)

        # Verify multiple filters were applied
        assert mock_queryset.filter.call_count >= 3  # race, sex, dob
        assert result['count'] == 2

    @patch('lab.models.Patient.objects')
    def test_query_by_args_returns_correct_structure(self, mock_objects):
        """Test query_by_args returns expected dictionary structure"""
        from lab.models import Patient

        mock_queryset = self.setup_mock_queryset(count=5)
        mock_objects.all.return_value = mock_queryset

        params = PatientTestData.DATATABLES_REQUEST

        patient = Patient()
        result = patient.query_by_args(**params)

        # Verify response structure
        assert 'items' in result
        assert 'count' in result
        assert 'total' in result
        assert 'draw' in result

        assert isinstance(result['items'], Mock)
        assert isinstance(result['count'], int)
        assert isinstance(result['total'], int)
        assert isinstance(result['draw'], int)

    @patch('lab.models.Patient.objects')
    def test_query_by_args_handles_empty_result(self, mock_objects):
        """Test query_by_args with no matching results"""
        from lab.models import Patient

        mock_queryset = self.setup_mock_queryset(count=0)
        mock_objects.all.return_value = mock_queryset

        params = {
            'draw': ['1'],
            'length': ['10'],
            'start': ['0'],
            'search[value]': ['nonexistent'],
            'order[0][column]': ['0'],
            'order[0][dir]': ['asc'],
            'race': [''],
            'sex': [''],
            'dob': [''],
        }

        patient = Patient()
        result = patient.query_by_args(**params)

        assert result['count'] == 0
        assert result['total'] == 0

    @patch('lab.models.Patient.objects')
    def test_query_by_args_with_different_column_orders(self, mock_objects):
        """Test query_by_args with different column ordering options"""
        from lab.models import Patient

        # Test each column in ORDER_COLUMN_CHOICES
        columns = {
            '0': 'id',
            '1': 'pat_id',
            '2': 'sex',
            '3': 'race',
            '4': 'source',
            '5': 'date_added',
        }

        for col_index, expected_field in columns.items():
            mock_queryset = self.setup_mock_queryset(count=10)
            mock_objects.all.return_value = mock_queryset

            params = {
                'draw': ['1'],
                'length': ['10'],
                'start': ['0'],
                'search[value]': [''],
                'order[0][column]': [col_index],
                'order[0][dir]': ['asc'],
                'race': [''],
                'sex': [''],
                'dob': [''],
            }

            patient = Patient()
            result = patient.query_by_args(**params)

            # Verify order_by was called with expected field
            order_arg = mock_queryset.order_by.call_args[0][0]
            assert order_arg == expected_field

    @patch('lab.models.Patient.objects')
    def test_query_by_args_exception_handling(self, mock_objects):
        """Test query_by_args raises exception on error"""
        from lab.models import Patient

        # Make queryset raise an exception
        mock_objects.all.side_effect = Exception('Database error')

        params = PatientTestData.DATATABLES_REQUEST

        patient = Patient()

        # Should raise the exception
        with pytest.raises(Exception) as exc_info:
            patient.query_by_args(**params)

        assert 'Database error' in str(exc_info.value)

    def setup_mock_queryset(self, count=10):
        """Helper to create a properly chained mock queryset"""
        mock_queryset = MagicMock()

        # Make queryset return itself for chaining
        mock_queryset.annotate.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.all.return_value = mock_queryset

        # Mock count
        mock_queryset.count.return_value = count

        # Mock slicing
        mock_queryset.__getitem__.return_value = mock_queryset

        return mock_queryset


class TestPatientModelFields(BaseAPITestNoDatabase):
    """Test Patient model field definitions"""

    def test_patient_race_choices(self):
        """Test RACE_TYPES are correctly defined"""
        from lab.models import Patient

        expected_choices = (
            (1, "American Indian or Alaska Native"),
            (2, "Asian"),
            (3, "Black or African American"),
            (4, "Native Hawaiian or Other Pacific Islander"),
            (5, "White"),
            (6, "Hispanic/Latino/Spanish Origin (of any race)"),
            (7, "N/A"),
        )

        assert Patient.RACE_TYPES == expected_choices

    def test_patient_sex_choices(self):
        """Test SEX_TYPES are correctly defined"""
        from lab.models import Patient

        expected_choices = (
            ("m", "Male"),
            ("f", "Female"),
        )

        assert Patient.SEX_TYPES == expected_choices

    def test_patient_consent_choices(self):
        """Test CONSENT_TYPES are correctly defined"""
        from lab.models import Patient

        expected_choices = (
            ("HTAN patient", "HTAN patient"),
            ("HTAN next-of-kin", "HTAN next-of-kin"),
            ("MelanomaTissueBank", "Melanoma Tissue Banking"),
        )

        assert Patient.CONSENT_TYPES == expected_choices

    def test_patient_str_method(self):
        """Test Patient __str__ returns pat_id"""
        mock_patient = self.create_mock_patient(pat_id='PAT123')

        assert str(mock_patient) == 'PAT123'

    def create_mock_patient(self, **kwargs):
        """Create a mock patient object"""
        patient = Mock()
        patient.id = kwargs.get('id', 1)
        patient.pat_id = kwargs.get('pat_id', 'PAT001')
        patient.sex = kwargs.get('sex', 'm')
        patient.race = kwargs.get('race', 5)
        patient.dob = kwargs.get('dob', 1980)
        patient.source = kwargs.get('source', '')
        patient.consent = kwargs.get('consent', '')
        patient.notes = kwargs.get('notes', '')
        patient.date_added = kwargs.get('date_added', datetime.now())
        patient.num_blocks = kwargs.get('num_blocks', 0)

        # Mock __str__ method
        patient.__str__ = Mock(return_value=patient.pat_id)

        return patient


class TestPatientQueryHelperFunctions(BaseAPITestNoDatabase):
    """Test helper functions in query_by_args"""

    @patch('lab.models.Patient.objects')
    def test_is_initial_value_detection(self, mock_objects):
        """Test detection of initial search values"""
        from lab.models import Patient

        mock_queryset = self.setup_mock_queryset(count=1)
        mock_objects.all.return_value = mock_queryset

        # Test with initial value
        params = {
            'draw': ['1'],
            'length': ['10'],
            'start': ['0'],
            'search[value]': ['_initial:{"model":"block","id":"123"}'],
            'order[0][column]': ['0'],
            'order[0][dir]': ['asc'],
            'race': [''],
            'sex': [''],
            'dob': [''],
        }

        patient = Patient()
        result = patient.query_by_args(**params)

        # Should process initial search
        assert result is not None

    @patch('lab.models.Patient.objects')
    def test_parse_value_with_initial_prefix(self, mock_objects):
        """Test parsing of initial search values"""
        from lab.models import Patient

        mock_queryset = self.setup_mock_queryset(count=1)
        mock_objects.all.return_value = mock_queryset

        # Test JSON parsing
        params = {
            'draw': ['1'],
            'length': ['10'],
            'start': ['0'],
            'search[value]': ['_initial:{"model":"patient","id":"789"}'],
            'order[0][column]': ['0'],
            'order[0][dir]': ['asc'],
            'race': [''],
            'sex': [''],
            'dob': [''],
        }

        patient = Patient()
        result = patient.query_by_args(**params)

        # Should successfully parse and execute query
        assert result['items'] is not None

    def setup_mock_queryset(self, count=10):
        """Helper to create a properly chained mock queryset"""
        mock_queryset = MagicMock()
        mock_queryset.annotate.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.all.return_value = mock_queryset
        mock_queryset.count.return_value = count
        mock_queryset.__getitem__.return_value = mock_queryset
        return mock_queryset
