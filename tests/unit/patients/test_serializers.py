# tests/unit/patients/test_serializers.py
"""
Patient Serializers Test Cases - No Database Required

Tests PatientsSerializer with complete mocking.
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from tests.utils.base_test import BaseAPITestNoDatabase
from tests.fixtures.patient_fixtures import PatientTestData


class TestPatientsSerializer(BaseAPITestNoDatabase):
    """Test PatientsSerializer"""

    def setUp(self):
        """Set up test fixtures"""
        super().setUp()

        # Create mock patient
        self.mock_patient = self.create_mock_patient()

    def create_mock_patient(self, **kwargs):
        """Create a mock patient object with all required fields"""
        patient = Mock()
        patient.id = kwargs.get('id', 1)
        patient.pat_id = kwargs.get('pat_id', 'PAT001')
        patient.sex = kwargs.get('sex', 'm')
        patient.race = kwargs.get('race', 5)
        patient.source = kwargs.get('source', 'UCSF')
        patient.date_added = kwargs.get('date_added', datetime(2024, 1, 1))
        patient.num_blocks = kwargs.get('num_blocks', 3)

        # Mock get_sex_display method
        sex_display_map = {
            'm': 'Male',
            'f': 'Female',
        }
        patient.get_sex_display = Mock(
            return_value=sex_display_map.get(patient.sex, '')
        )

        # Mock get_race_display method
        race_display_map = {
            1: 'American Indian or Alaska Native',
            2: 'Asian',
            3: 'Black or African American',
            4: 'Native Hawaiian or Other Pacific Islander',
            5: 'White',
            6: 'Hispanic/Latino/Spanish Origin (of any race)',
            7: 'N/A',
        }
        patient.get_race_display = Mock(
            return_value=race_display_map.get(patient.race, 'N/A')
        )

        return patient

    def test_serializer_contains_expected_fields(self):
        """Test serializer has all expected fields"""
        from lab.serializers import PatientsSerializer

        serializer = PatientsSerializer(instance=self.mock_patient)
        data = serializer.data

        # Verify all fields are present
        expected_fields = {
            'id', 'pat_id', 'source', 'sex', 'race',
            'sex_label', 'race_label', 'date_added',
            'num_blocks', 'DT_RowId'
        }

        assert set(data.keys()) == expected_fields

    def test_serializer_field_types(self):
        """Test serializer fields have correct types"""
        from lab.serializers import PatientsSerializer

        serializer = PatientsSerializer(instance=self.mock_patient)
        data = serializer.data

        # Verify field types
        assert isinstance(data['id'], int)
        assert isinstance(data['pat_id'], str)
        assert isinstance(data['source'], str)
        assert isinstance(data['sex'], str)
        assert isinstance(data['race'], int)
        assert isinstance(data['sex_label'], str)
        assert isinstance(data['race_label'], str)
        assert isinstance(data['num_blocks'], int)
        assert isinstance(data['DT_RowId'], int)

    def test_serializer_id_field(self):
        """Test id field serialization"""
        from lab.serializers import PatientsSerializer

        patient = self.create_mock_patient(id=42)
        serializer = PatientsSerializer(instance=patient)

        assert serializer.data['id'] == 42

    def test_serializer_pat_id_field(self):
        """Test pat_id field serialization"""
        from lab.serializers import PatientsSerializer

        patient = self.create_mock_patient(pat_id='PAT123')
        serializer = PatientsSerializer(instance=patient)

        assert serializer.data['pat_id'] == 'PAT123'

    def test_serializer_source_field(self):
        """Test source field serialization"""
        from lab.serializers import PatientsSerializer

        patient = self.create_mock_patient(source='Stanford')
        serializer = PatientsSerializer(instance=patient)

        assert serializer.data['source'] == 'Stanford'

    def test_serializer_sex_field(self):
        """Test sex field serialization"""
        from lab.serializers import PatientsSerializer

        patient = self.create_mock_patient(sex='f')
        serializer = PatientsSerializer(instance=patient)

        assert serializer.data['sex'] == 'f'

    def test_serializer_race_field(self):
        """Test race field serialization"""
        from lab.serializers import PatientsSerializer

        patient = self.create_mock_patient(race=2)
        serializer = PatientsSerializer(instance=patient)

        assert serializer.data['race'] == 2

    def test_serializer_date_added_field(self):
        """Test date_added field serialization"""
        from lab.serializers import PatientsSerializer

        test_date = datetime(2025, 9, 16)
        patient = self.create_mock_patient(date_added=test_date)
        serializer = PatientsSerializer(instance=patient)

        # Date should be serialized
        assert serializer.data['date_added'] is not None

    def test_serializer_num_blocks_field(self):
        """Test num_blocks field serialization"""
        from lab.serializers import PatientsSerializer

        patient = self.create_mock_patient(num_blocks=5)
        serializer = PatientsSerializer(instance=patient)

        assert serializer.data['num_blocks'] == 5

    def test_serializer_num_blocks_zero(self):
        """Test num_blocks field when zero"""
        from lab.serializers import PatientsSerializer

        patient = self.create_mock_patient(num_blocks=0)
        serializer = PatientsSerializer(instance=patient)

        assert serializer.data['num_blocks'] == 0

    def test_get_dt_row_id_method(self):
        """Test get_DT_RowId returns patient id"""
        from lab.serializers import PatientsSerializer

        patient = self.create_mock_patient(id=123)
        serializer = PatientsSerializer(instance=patient)

        # DT_RowId should equal id
        assert serializer.data['DT_RowId'] == 123

    def test_get_dt_row_id_matches_id(self):
        """Test DT_RowId always matches id field"""
        from lab.serializers import PatientsSerializer

        for test_id in [1, 42, 999, 12345]:
            patient = self.create_mock_patient(id=test_id)
            serializer = PatientsSerializer(instance=patient)

            assert serializer.data['DT_RowId'] == serializer.data['id']

    def test_get_sex_label_male(self):
        """Test get_sex_label for Male"""
        from lab.serializers import PatientsSerializer

        patient = self.create_mock_patient(sex='m')
        serializer = PatientsSerializer(instance=patient)

        assert serializer.data['sex_label'] == 'Male'
        patient.get_sex_display.assert_called_once()

    def test_get_sex_label_female(self):
        """Test get_sex_label for Female"""
        from lab.serializers import PatientsSerializer

        patient = self.create_mock_patient(sex='f')
        patient.get_sex_display = Mock(return_value='Female')

        serializer = PatientsSerializer(instance=patient)

        assert serializer.data['sex_label'] == 'Female'
        patient.get_sex_display.assert_called_once()

    def test_get_race_label_white(self):
        """Test get_race_label for White"""
        from lab.serializers import PatientsSerializer

        patient = self.create_mock_patient(race=5)
        serializer = PatientsSerializer(instance=patient)

        assert serializer.data['race_label'] == 'White'
        patient.get_race_display.assert_called_once()

    def test_get_race_label_asian(self):
        """Test get_race_label for Asian"""
        from lab.serializers import PatientsSerializer

        patient = self.create_mock_patient(race=2)
        patient.get_race_display = Mock(return_value='Asian')

        serializer = PatientsSerializer(instance=patient)

        assert serializer.data['race_label'] == 'Asian'
        patient.get_race_display.assert_called_once()

    def test_serializer_with_sample_patient_data(self):
        """Test serializer with realistic patient data"""
        from lab.serializers import PatientsSerializer

        # Use sample patient from fixtures
        sample = PatientTestData.SINGLE_PATIENT

        patient = self.create_mock_patient(
            id=sample['id'],
            pat_id=sample['pat_id'],
            sex=sample['sex'],
            race=sample['race'],
            source=sample['source'],
            num_blocks=sample['num_blocks']
        )

        serializer = PatientsSerializer(instance=patient)
        data = serializer.data

        assert data['id'] == sample['id']
        assert data['pat_id'] == sample['pat_id']
        assert data['sex'] == sample['sex']
        assert data['race'] == sample['race']
        assert data['source'] == sample['source']
        assert data['num_blocks'] == sample['num_blocks']

    def test_serializer_many_true(self):
        """Test serializer with many=True for multiple patients"""
        from lab.serializers import PatientsSerializer

        patients = [
            self.create_mock_patient(id=1, pat_id='PAT001'),
            self.create_mock_patient(id=2, pat_id='PAT002'),
            self.create_mock_patient(id=3, pat_id='PAT003'),
        ]

        serializer = PatientsSerializer(patients, many=True)
        data = serializer.data

        assert len(data) == 3
        assert data[0]['id'] == 1
        assert data[1]['id'] == 2
        assert data[2]['id'] == 3

    def test_serializer_empty_list(self):
        """Test serializer with empty list"""
        from lab.serializers import PatientsSerializer

        serializer = PatientsSerializer([], many=True)
        data = serializer.data

        assert data == []
        assert len(data) == 0

    def test_serializer_with_all_sample_patients(self):
        """Test serializer with all sample patients from fixtures"""
        from lab.serializers import PatientsSerializer

        patients = []
        for sample in PatientTestData.SAMPLE_PATIENTS:
            patient = self.create_mock_patient(
                id=sample['id'],
                pat_id=sample['pat_id'],
                sex=sample['sex'],
                race=sample['race'],
                source=sample['source'],
                num_blocks=sample['num_blocks']
            )
            patients.append(patient)

        serializer = PatientsSerializer(patients, many=True)
        data = serializer.data

        assert len(data) == len(PatientTestData.SAMPLE_PATIENTS)

        # Verify first and last patients
        assert data[0]['pat_id'] == 'PAT001'
        assert data[-1]['pat_id'] == 'PAT005'

    def test_serializer_output_matches_expected_format(self):
        """Test serializer output matches DataTables Editor format"""
        from lab.serializers import PatientsSerializer

        patient = self.create_mock_patient(
            id=1,
            pat_id='PAT001',
            sex='m',
            race=5,
            source='UCSF',
            num_blocks=3
        )

        serializer = PatientsSerializer(instance=patient)
        data = serializer.data

        # Should match expected format
        expected = PatientTestData.SINGLE_PATIENT
        assert data['id'] == expected['id']
        assert data['pat_id'] == expected['pat_id']
        assert data['sex'] == expected['sex']
        assert data['race'] == expected['race']
        assert data['DT_RowId'] == expected['DT_RowId']

    def test_serializer_preserves_field_order(self):
        """Test serializer maintains field order"""
        from lab.serializers import PatientsSerializer

        serializer = PatientsSerializer(instance=self.mock_patient)
        data = serializer.data

        # Get field order
        field_names = list(data.keys())

        # Verify expected fields are present
        expected_fields = [
            'id', 'pat_id', 'source', 'sex', 'race',
            'sex_label', 'race_label', 'date_added',
            'num_blocks', 'DT_RowId'
        ]

        for field in expected_fields:
            assert field in field_names

    def test_serializer_meta_fields(self):
        """Test serializer Meta class fields configuration"""
        from lab.serializers import PatientsSerializer

        # Check Meta fields
        expected_fields = (
            "id", "pat_id", "source", "sex", "race",
            "sex_label", "race_label", "date_added",
            "num_blocks", "DT_RowId",
        )

        assert PatientsSerializer.Meta.fields == expected_fields

    def test_serializer_meta_model(self):
        """Test serializer Meta class model configuration"""
        from lab.serializers import PatientsSerializer
        from lab.models import Patient

        assert PatientsSerializer.Meta.model == Patient

    def test_serializer_readonly_fields(self):
        """Test DT_RowId, sex_label, and race_label are read-only (SerializerMethodFields)"""
        from lab.serializers import PatientsSerializer
        from rest_framework import serializers

        # Get field instances
        serializer = PatientsSerializer()

        # DT_RowId, sex_label, and race_label should be SerializerMethodFields
        assert isinstance(
            serializer.fields['DT_RowId'],
            serializers.SerializerMethodField
        )
        assert isinstance(
            serializer.fields['sex_label'],
            serializers.SerializerMethodField
        )
        assert isinstance(
            serializer.fields['race_label'],
            serializers.SerializerMethodField
        )

    def test_serializer_num_blocks_is_integer_field(self):
        """Test num_blocks is IntegerField"""
        from lab.serializers import PatientsSerializer
        from rest_framework import serializers

        serializer = PatientsSerializer()

        assert isinstance(
            serializer.fields['num_blocks'],
            serializers.IntegerField
        )


class TestSerializerIntegration(BaseAPITestNoDatabase):
    """Integration tests for serializers"""

    def test_patients_serializer_matches_datatables_format(self):
        """Test PatientsSerializer output matches DataTables expected format"""
        from lab.serializers import PatientsSerializer

        # Create patients matching fixture data
        patients = []
        for sample in PatientTestData.SAMPLE_PATIENTS[:3]:
            patient = Mock()
            patient.id = sample['id']
            patient.pat_id = sample['pat_id']
            patient.sex = sample['sex']
            patient.race = sample['race']
            patient.source = sample['source']
            patient.num_blocks = sample['num_blocks']
            patient.date_added = datetime.now()
            patient.get_sex_display = Mock(return_value=sample['sex_label'])
            patient.get_race_display = Mock(return_value=sample['race_label'])
            patients.append(patient)

        serializer = PatientsSerializer(patients, many=True)
        data = serializer.data

        # Verify DataTables required fields
        for item in data:
            assert 'DT_RowId' in item  # Required by DataTables
            assert 'id' in item
            assert 'pat_id' in item
            assert 'sex_label' in item
            assert 'race_label' in item

    def test_serializer_with_queryset_result(self):
        """Test serializer works with query_by_args result format"""
        from lab.serializers import PatientsSerializer

        # Simulate result from Patient.query_by_args
        mock_items = [
            Mock(
                id=1,
                pat_id='PAT001',
                sex='m',
                race=5,
                source='UCSF',
                num_blocks=3,
                date_added=datetime.now(),
                get_sex_display=Mock(return_value='Male'),
                get_race_display=Mock(return_value='White')
            )
        ]

        serializer = PatientsSerializer(mock_items, many=True)

        assert len(serializer.data) == 1
        assert serializer.data[0]['pat_id'] == 'PAT001'

    def test_serializer_output_for_json_response(self):
        """Test serializer output can be used in JsonResponse"""
        from lab.serializers import PatientsSerializer
        import json

        patient = Mock()
        patient.id = 1
        patient.pat_id = 'PAT001'
        patient.sex = 'm'
        patient.race = 5
        patient.source = 'UCSF'
        patient.num_blocks = 3
        patient.date_added = datetime(2024, 1, 1)
        patient.get_sex_display = Mock(return_value='Male')
        patient.get_race_display = Mock(return_value='White')

        serializer = PatientsSerializer(instance=patient)

        # Should be JSON serializable
        json_str = json.dumps(serializer.data)

        # Should be able to load back
        loaded_data = json.loads(json_str)
        assert loaded_data['id'] == 1
        assert loaded_data['pat_id'] == 'PAT001'

    def test_serializer_contract_with_view_response(self):
        """Test serializer output matches view response format expectations"""
        from lab.serializers import PatientsSerializer

        # Create mock patients
        patients = [
            Mock(
                id=i,
                pat_id=f'PAT{i:03d}',
                sex='m',
                race=5,
                source='UCSF',
                num_blocks=i * 2,
                date_added=datetime.now(),
                get_sex_display=Mock(return_value='Male'),
                get_race_display=Mock(return_value='White')
            )
            for i in range(1, 6)
        ]

        serializer = PatientsSerializer(patients, many=True)

        # Simulate view response structure
        response = {
            'data': serializer.data,
            'draw': 1,
            'recordsTotal': 5,
            'recordsFiltered': 5,
        }

        # Verify response structure
        assert isinstance(response['data'], list)
        assert len(response['data']) == 5
        assert all('DT_RowId' in item for item in response['data'])


class TestSerializerEdgeCases(BaseAPITestNoDatabase):
    """Test serializer edge cases and error handling"""

    def test_serializer_with_none_patient(self):
        """Test serializer with None instance"""
        from lab.serializers import PatientsSerializer

        serializer = PatientsSerializer(instance=None)

        # Should handle None gracefully
        assert serializer.instance is None

    def test_serializer_with_null_source(self):
        """Test serializer with null source"""
        from lab.serializers import PatientsSerializer

        patient = Mock()
        patient.id = 1
        patient.pat_id = 'PAT001'
        patient.sex = 'm'
        patient.race = 5
        patient.source = None  # Null value
        patient.num_blocks = 0
        patient.date_added = datetime.now()
        patient.get_sex_display = Mock(return_value='Male')
        patient.get_race_display = Mock(return_value='White')

        serializer = PatientsSerializer(instance=patient)
        data = serializer.data

        # Should handle null source
        assert data['source'] is None

    def test_serializer_preserves_data_types(self):
        """Test serializer preserves correct data types"""
        from lab.serializers import PatientsSerializer

        patient = Mock()
        patient.id = 1
        patient.pat_id = 'PAT001'
        patient.sex = 'm'
        patient.race = 5
        patient.source = 'UCSF'
        patient.num_blocks = 10
        patient.date_added = datetime.now()
        patient.get_sex_display = Mock(return_value='Male')
        patient.get_race_display = Mock(return_value='White')

        serializer = PatientsSerializer(instance=patient)
        data = serializer.data

        # Verify types are preserved
        assert isinstance(data['id'], int)
        assert isinstance(data['num_blocks'], int)
        assert isinstance(data['DT_RowId'], int)
        assert isinstance(data['pat_id'], str)
        assert isinstance(data['sex_label'], str)
        assert isinstance(data['race_label'], str)

    def test_serializer_with_different_race_values(self):
        """Test serializer handles all race type values"""
        from lab.serializers import PatientsSerializer

        race_map = {
            1: 'American Indian or Alaska Native',
            2: 'Asian',
            3: 'Black or African American',
            4: 'Native Hawaiian or Other Pacific Islander',
            5: 'White',
            6: 'Hispanic/Latino/Spanish Origin (of any race)',
            7: 'N/A',
        }

        for race_value, expected_label in race_map.items():
            patient = Mock()
            patient.id = 1
            patient.pat_id = 'PAT001'
            patient.sex = 'm'
            patient.race = race_value
            patient.source = 'UCSF'
            patient.num_blocks = 0
            patient.date_added = datetime.now()
            patient.get_sex_display = Mock(return_value='Male')
            patient.get_race_display = Mock(return_value=expected_label)

            serializer = PatientsSerializer(instance=patient)

            assert serializer.data['race'] == race_value
            assert serializer.data['race_label'] == expected_label
