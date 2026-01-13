# tests/fixtures/libprep_fixtures.py
"""
Libprep Test Fixtures - Centralized test data for Libprep operations
"""
from datetime import datetime


class LibprepTestData:
    """Centralized test data for Libprep operations"""

    # NA Types
    NA_TYPES = [
        ("dna", "DNA"),
        ("rna", "RNA"),
        ("both", "Both DNA and RNA"),
    ]

    # Sample NucAcid
    SAMPLE_NUCACID = {
        'id': 1,
        'name': 'BLK001_area1-D-1',
        'date': datetime.now(),
        'method_id': 1,
        'na_type': 'dna',
        'conc': 25.5,
        'vol_init': 50.0,
        'vol_remain': 45.0,
        'notes': 'Test nucleic acid',
    }

    # Multiple NucAcids
    SAMPLE_NUCACIDS = [
        {
            'id': 1,
            'name': 'BLK001_area1-D-1',
            'na_type': 'dna',
            'conc': 25.5,
            'vol_init': 50.0,
            'vol_remain': 45.0,
        },
        {
            'id': 2,
            'name': 'BLK001_area2-R-1',
            'na_type': 'rna',
            'conc': 30.0,
            'vol_init': 40.0,
            'vol_remain': 35.0,
        },
        {
            'id': 3,
            'name': 'BLK002_area1-D-1',
            'na_type': 'dna',
            'conc': 20.0,
            'vol_init': 60.0,
            'vol_remain': 55.0,
        },
    ]

    # Sample AREA_NA_LINK
    SAMPLE_AREA_NA_LINK = {
        'id': 1,
        'nucacid_id': 1,
        'area_id': 1,
        'input_vol': 5.0,
        'input_amount': 127.5,
        'date': datetime.now(),
    }

    # DataTables request parameters
    DATATABLES_REQUEST = {
        'draw': ['1'],
        'start': ['0'],
        'length': ['10'],
        'search[value]': [''],
        'order[0][column]': ['0'],
        'order[0][dir]': ['asc'],
        'date_range': [''],
        'na_type': [''],
    }

    # Form data for NucAcidForm
    NUCACID_FORM_DATA = {
        'name': 'TEST_NA-D-1',
        'date': datetime.now(),
        'method': 1,
        'na_type': 'dna',
        'conc': 25.5,
        'vol_init': 50.0,
        'vol_remain': 50.0,
        'notes': 'Test notes',
        'area': [1, 2],
        'amount': 127.5,
    }

    # SampleLibCreationOptionsForm data
    SAMPLELIB_OPTIONS_FORM_DATA = {
        'barcode_start_with': 1,
        'target_amount': 100.0,
        'shear_volume': 50.0,
        'prefix': 'LIB',
    }

    # FilterForm data
    FILTER_FORM_DATA = {
        'date_range': '2024-01-01 to 2024-12-31',
        'na_type': 'dna',
    }
