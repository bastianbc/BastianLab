# tests/fixtures/patient_fixtures.py
"""
Shared test data for Patient testing - ensures consistency across all test layers
"""
from datetime import datetime


class PatientTestData:
    """Centralized test data for Patients"""

    # Valid patient data that should work across all layers
    VALID_PATIENT_DATA = {
        'pat_id': 'PAT001',
        'sex': 'm',
        'race': 5,
        'dob': 1980,
        'source': 'Test Hospital',
        'consent': 'HTAN patient',
        'notes': 'Test patient notes',
    }

    # Sample patients matching realistic data
    SAMPLE_PATIENTS = [
        {
            'id': 1,
            'pat_id': 'PAT001',
            'sex': 'm',
            'sex_label': 'Male',
            'race': 5,
            'race_label': 'White',
            'source': 'UCSF',
            'date_added': '2024-01-15T10:30:00Z',
            'num_blocks': 3,
            'DT_RowId': 1,
        },
        {
            'id': 2,
            'pat_id': 'PAT002',
            'sex': 'f',
            'sex_label': 'Female',
            'race': 2,
            'race_label': 'Asian',
            'source': 'Stanford',
            'date_added': '2024-02-20T14:15:00Z',
            'num_blocks': 5,
            'DT_RowId': 2,
        },
        {
            'id': 3,
            'pat_id': 'PAT003',
            'sex': 'm',
            'sex_label': 'Male',
            'race': 3,
            'race_label': 'Black or African American',
            'source': 'Kaiser',
            'date_added': '2024-03-10T09:00:00Z',
            'num_blocks': 0,
            'DT_RowId': 3,
        },
        {
            'id': 4,
            'pat_id': 'PAT004',
            'sex': 'f',
            'sex_label': 'Female',
            'race': 6,
            'race_label': 'Hispanic/Latino/Spanish Origin (of any race)',
            'source': 'UCSF',
            'date_added': '2024-04-05T11:45:00Z',
            'num_blocks': 8,
            'DT_RowId': 4,
        },
        {
            'id': 5,
            'pat_id': 'PAT005',
            'sex': 'm',
            'sex_label': 'Male',
            'race': 1,
            'race_label': 'American Indian or Alaska Native',
            'source': 'Community Hospital',
            'date_added': '2024-05-12T16:20:00Z',
            'num_blocks': 2,
            'DT_RowId': 5,
        },
    ]

    # DataTables request format (what JS sends)
    DATATABLES_REQUEST = {
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

    # Expected response format (what views should return)
    DATATABLES_RESPONSE = {
        'draw': 1,
        'recordsTotal': 5,
        'recordsFiltered': 5,
        'data': SAMPLE_PATIENTS
    }

    # Expected DataTables response with all fields (matching serializer)
    @staticmethod
    def get_datatables_response_with_patients():
        """Returns a complete DataTables response with sample patients"""
        return {
            'draw': 1,
            'recordsTotal': len(PatientTestData.SAMPLE_PATIENTS),
            'recordsFiltered': len(PatientTestData.SAMPLE_PATIENTS),
            'data': PatientTestData.SAMPLE_PATIENTS
        }

    # Single patient for testing
    SINGLE_PATIENT = {
        'id': 1,
        'pat_id': 'PAT001',
        'sex': 'm',
        'sex_label': 'Male',
        'race': 5,
        'race_label': 'White',
        'source': 'UCSF',
        'date_added': '2024-01-15T10:30:00Z',
        'num_blocks': 3,
        'DT_RowId': 1,
    }

    # Patient with no blocks
    PATIENT_NO_BLOCKS = {
        'id': 3,
        'pat_id': 'PAT003',
        'sex': 'm',
        'sex_label': 'Male',
        'race': 3,
        'race_label': 'Black or African American',
        'source': 'Kaiser',
        'date_added': '2024-03-10T09:00:00Z',
        'num_blocks': 0,
        'DT_RowId': 3,
    }

    # Patient with many blocks
    PATIENT_MANY_BLOCKS = {
        'id': 4,
        'pat_id': 'PAT004',
        'sex': 'f',
        'sex_label': 'Female',
        'race': 6,
        'race_label': 'Hispanic/Latino/Spanish Origin (of any race)',
        'source': 'UCSF',
        'date_added': '2024-04-05T11:45:00Z',
        'num_blocks': 8,
        'DT_RowId': 4,
    }

    # Race types (matching Patient.RACE_TYPES)
    RACE_TYPES = (
        (1, "American Indian or Alaska Native"),
        (2, "Asian"),
        (3, "Black or African American"),
        (4, "Native Hawaiian or Other Pacific Islander"),
        (5, "White"),
        (6, "Hispanic/Latino/Spanish Origin (of any race)"),
        (7, "N/A"),
    )

    # Sex types (matching Patient.SEX_TYPES)
    SEX_TYPES = (
        ("m", "Male"),
        ("f", "Female"),
    )

    # Consent types (matching Patient.CONSENT_TYPES)
    CONSENT_TYPES = (
        ("HTAN patient", "HTAN patient"),
        ("HTAN next-of-kin", "HTAN next-of-kin"),
        ("MelanomaTissueBank", "Melanoma Tissue Banking"),
    )
