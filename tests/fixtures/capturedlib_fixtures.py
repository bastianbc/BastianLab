# tests/fixtures/capturedlib_fixtures.py
"""
Capturedlib Test Data Fixtures
"""
from datetime import datetime


class CapturedlibTestData:
    """Centralized test data for Capturedlib operations"""

    SAMPLE_CAPTUREDLIB = {
        'id': 1,
        'name': 'CL-001',
        'date': datetime.now(),
        'bait_id': 1,
        'frag_size': 450.5,
        'conc': 25.8,
        'amp_cycle': 12,
        'buffer_id': 1,
        'nm': 175.6,
        'vol_init': 50.0,
        'vol_remain': 45.0,
        'notes': 'Test captured library',
    }

    SAMPLE_CAPTUREDLIBS = [
        {
            'id': 1,
            'name': 'CL-001',
            'date': datetime.now(),
            'bait_id': 1,
            'frag_size': 450.5,
            'conc': 25.8,
            'amp_cycle': 12,
            'nm': 175.6,
            'vol_init': 50.0,
            'vol_remain': 45.0,
        },
        {
            'id': 2,
            'name': 'CL-002',
            'date': datetime.now(),
            'bait_id': 2,
            'frag_size': 380.2,
            'conc': 30.5,
            'amp_cycle': 10,
            'nm': 200.3,
            'vol_init': 60.0,
            'vol_remain': 55.0,
        },
        {
            'id': 3,
            'name': 'CL-003',
            'date': datetime.now(),
            'bait_id': 1,
            'frag_size': 500.0,
            'conc': 22.4,
            'amp_cycle': 14,
            'nm': 150.8,
            'vol_init': 40.0,
            'vol_remain': 38.0,
        },
    ]

    SAMPLE_SL_CL_LINK = {
        'id': 1,
        'captured_lib_id': 1,
        'sample_lib_id': 1,
        'volume': 10.5,
        'date': datetime.now(),
    }

    SAMPLE_SL_CL_LINKS = [
        {
            'id': 1,
            'captured_lib_id': 1,
            'sample_lib_id': 1,
            'volume': 10.5,
            'date': datetime.now(),
        },
        {
            'id': 2,
            'captured_lib_id': 1,
            'sample_lib_id': 2,
            'volume': 12.0,
            'date': datetime.now(),
        },
    ]

    DATATABLES_REQUEST = {
        'draw': ['1'],
        'length': ['10'],
        'start': ['0'],
        'search[value]': [''],
        'order[0][column]': ['1'],
        'order[0][dir]': ['asc'],
        'normal_area': [''],
        'bait': [''],
    }

    CAPTUREDLIB_FORM_DATA = {
        'name': 'CL-Test-001',
        'date': '2024-01-15',
        'bait': 1,
        'frag_size': 450.5,
        'conc': 25.8,
        'amp_cycle': 12,
        'buffer': 1,
        'nm': 175.6,
        'vol_init': 50.0,
        'vol_remain': 45.0,
        'notes': 'Test notes',
        'sample_lib': [1, 2],
    }

    SEQUENCINGLIB_CREATION_FORM_DATA = {
        'sequencing_lib': 1,
        'prefix': 'SEQL',
        'date': '2024-01-15',
        'buffer': 'TE',
        'nm': 2.0,
        'vol_init': 30.0,
    }

    FILTER_FORM_DATA = {
        'area_type': 'normal',
        'bait': 1,
    }
