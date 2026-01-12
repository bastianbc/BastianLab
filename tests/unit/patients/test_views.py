# tests/unit/patients/test_views.py
"""
Patient Views Test Cases - No Database Required
"""
import json
from unittest.mock import Mock, patch, PropertyMock
from django.http import JsonResponse
from tests.utils.base_test import BaseAPITestNoDatabase
from tests.fixtures.patient_fixtures import PatientTestData

# Import views at module level to avoid patching issues
from lab.views import filter_patients, get_race_options, get_sex_options, get_race


class TestFilterPatientsView(BaseAPITestNoDatabase):
    """Test filter_patients view without database"""

    def test_filter_patients_returns_datatable_format(self):
        """Test filter_patients returns correct DataTables format"""
        # Grant permission to user
        self.grant_permission(self.user, 'lab.view_patient')

        # Mock Patient().query_by_args and serializer
        with patch('lab.views.Patient') as mock_patient_class, \
             patch('lab.serializers.PatientsSerializer') as mock_serializer_class:

            # Mock Patient().query_by_args
            mock_patient_instance = Mock()
            mock_patient_instance.query_by_args.return_value = {
                'items': [],
                'count': 5,
                'total': 5,
                'draw': 1
            }
            mock_patient_class.return_value = mock_patient_instance

            # Mock serializer - configure data attribute explicitly
            mock_serializer_class.return_value.data = PatientTestData.SAMPLE_PATIENTS

            # Create request with GET parameters
            request = self.create_request(
                method='GET',
                path='/lab/filter_patients',
                get_params=PatientTestData.DATATABLES_REQUEST,
                user=self.user
            )

            # Call view
            response = filter_patients(request)

            # Assertions
            self.assertJSONResponse(response, 200)
            data = json.loads(response.content)

            assert 'data' in data
            assert 'draw' in data
            assert 'recordsTotal' in data
            assert 'recordsFiltered' in data

            assert data['draw'] == 1
            assert data['recordsTotal'] == 5
            assert data['recordsFiltered'] == 5
            assert len(data['data']) == len(PatientTestData.SAMPLE_PATIENTS)


class TestGetRaceOptionsView(BaseAPITestNoDatabase):
    """Test get_race_options view"""

    def test_get_race_options_returns_json(self):
        """Test get_race_options returns JSON response"""
        with patch('lab.views.Patient') as mock_patient_class:
            # Mock RACE_TYPES
            mock_patient_class.RACE_TYPES = PatientTestData.RACE_TYPES

            request = self.create_request(method='GET', user=self.user)
            response = get_race_options(request)

            # Verify response type
            assert isinstance(response, JsonResponse)

    def test_get_race_options_includes_empty_option(self):
        """Test get_race_options includes empty option"""
        with patch('lab.views.Patient') as mock_patient_class:
            mock_patient_class.RACE_TYPES = PatientTestData.RACE_TYPES

            request = self.create_request(method='GET', user=self.user)
            response = get_race_options(request)

            data = json.loads(response.content)
            # First option should be empty
            assert data[0]['label'] == '---------'
            assert data[0]['value'] == ''


class TestGetSexOptionsView(BaseAPITestNoDatabase):
    """Test get_sex_options view"""

    def test_get_sex_options_returns_json(self):
        """Test get_sex_options returns JSON response"""
        with patch('lab.views.Patient') as mock_patient_class:
            # Mock SEX_TYPES
            mock_patient_class.SEX_TYPES = PatientTestData.SEX_TYPES

            request = self.create_request(method='GET', user=self.user)
            response = get_sex_options(request)

            # Verify response type
            assert isinstance(response, JsonResponse)

    def test_get_sex_options_includes_empty_option(self):
        """Test get_sex_options includes empty option"""
        with patch('lab.views.Patient') as mock_patient_class:
            mock_patient_class.SEX_TYPES = PatientTestData.SEX_TYPES

            request = self.create_request(method='GET', user=self.user)
            response = get_sex_options(request)

            data = json.loads(response.content)
            # First option should be empty
            assert data[0]['label'] == '---------'
            assert data[0]['value'] == ''


class TestGetRaceFunction(BaseAPITestNoDatabase):
    """Test get_race utility function"""

    def test_get_race_matches_valid_race(self):
        """Test get_race returns correct race ID for valid input"""
        with patch('lab.views.Patient') as mock_patient_class:
            mock_patient_class.RACE_TYPES = PatientTestData.RACE_TYPES

            result = get_race('White')
            assert result == 5

    def test_get_race_case_insensitive(self):
        """Test get_race is case insensitive"""
        with patch('lab.views.Patient') as mock_patient_class:
            mock_patient_class.RACE_TYPES = PatientTestData.RACE_TYPES

            result = get_race('white')
            assert result == 5

            result = get_race('WHITE')
            assert result == 5

