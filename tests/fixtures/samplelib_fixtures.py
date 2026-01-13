# tests/fixtures/samplelib_fixtures.py
"""
Samplelib Test Fixtures - Centralized test data for Samplelib operations
"""
from datetime import datetime


class SamplelibTestData:
    """Centralized test data for Samplelib operations"""

    # Sample SampleLib
    SAMPLE_SAMPLELIB = {
        'id': 1,
        'name': 'SL-001',
        'barcode_id': 1,
        'date': datetime.now(),
        'method_id': 1,
        'qubit': 25.5,
        'shear_volume': 50.0,
        'qpcr_conc': 30.0,
        'pcr_cycles': 12.0,
        'amount_in': 100.0,
        'amount_final': 95.0,
        'vol_init': 50.0,
        'vol_remain': 45.0,
        'notes': 'Test sample library',
    }

    # Multiple SampleLibs
    SAMPLE_SAMPLELIBS = [
        {
            'id': 1,
            'name': 'SL-001',
            'qubit': 25.5,
            'qpcr_conc': 30.0,
            'vol_init': 50.0,
            'vol_remain': 45.0,
        },
        {
            'id': 2,
            'name': 'SL-002',
            'qubit': 28.0,
            'qpcr_conc': 32.0,
            'vol_init': 60.0,
            'vol_remain': 55.0,
        },
        {
            'id': 3,
            'name': 'SL-003',
            'qubit': 22.0,
            'qpcr_conc': 28.0,
            'vol_init': 40.0,
            'vol_remain': 35.0,
        },
    ]

    # Sample NA_SL_LINK
    SAMPLE_NA_SL_LINK = {
        'id': 1,
        'nucacid_id': 1,
        'sample_lib_id': 1,
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
        'sequencing_run': [''],
        'barcode': [''],
        'i5': [''],
        'i7': [''],
        'area_type': [''],
        'bait': [''],
    }

    # Form data for SampleLibForm
    SAMPLELIB_FORM_DATA = {
        'name': 'SL-TEST',
        'barcode': 1,
        'date': datetime.now(),
        'method': 1,
        'qubit': 25.5,
        'shear_volume': 50.0,
        'qpcr_conc': 30.0,
        'pcr_cycles': 12.0,
        'amount_in': 100.0,
        'amount_final': 95.0,
        'vol_init': 50.0,
        'vol_remain': 50.0,
        'notes': 'Test notes',
        'nuc_acid': [1, 2],
        'captured_libs': [1],
    }

    # CapturedLibCreationOptionsForm data
    CAPTUREDLIB_OPTIONS_FORM_DATA = {
        'prefix': 'CL',
        'date': datetime.now().date(),
        'bait': 1,
    }

    # FilterForm data
    FILTER_FORM_DATA = {
        'sequencing_run': 1,
        'barcode': 1,
        'i5': 'ATCG',
        'i7': 'GCTA',
        'area_type': 'normal',
        'bait': 1,
    }

    # CapturedLibAddForm data
    CAPTUREDLIB_ADD_FORM_DATA = {
        'captured_lib': 1,
    }
