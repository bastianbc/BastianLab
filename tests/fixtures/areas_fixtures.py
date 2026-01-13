# tests/fixtures/areas_fixtures.py
"""
Shared test data for areas testing
"""
from datetime import datetime


class AreasTestData:
    """Centralized test data for Areas operations"""

    # Sample area data
    SAMPLE_AREA = {
        'id': 1,
        'name': 'BLK001_area1',
        'block_id': 1,
        'area_type_id': 1,
        'notes': 'Test notes',
        'collection': 'SC',
    }

    # Sample areas list
    SAMPLE_AREAS = [
        {
            'id': 1,
            'name': 'BLK001_area1',
            'block_id': 1,
            'area_type': 'Type A',
            'num_nucacids': 2,
            'num_samplelibs': 3,
            'num_variants': 10,
            'DT_RowId': 1,
        },
        {
            'id': 2,
            'name': 'BLK001_area2',
            'block_id': 1,
            'area_type': 'Type B',
            'num_nucacids': 1,
            'num_samplelibs': 2,
            'num_variants': 5,
            'DT_RowId': 2,
        },
    ]

    # DataTables request format
    DATATABLES_REQUEST = {
        'draw': ['1'],
        'length': ['10'],
        'start': ['0'],
        'search[value]': [''],
        'order[0][column]': ['1'],
        'order[0][dir]': ['asc'],
    }

    # Collection choices
    COLLECTION_CHOICES = [
        ('PU', 'Punch'),
        ('SC', 'Scraping'),
        ('PE', 'Cell Pellet'),
        ('CU', 'Curls'),
        ('FF', 'FFPE')
    ]

    # Area types
    AREA_TYPES = [
        {'id': 1, 'name': 'Type A'},
        {'id': 2, 'name': 'Type B'},
        {'id': 3, 'name': 'Type C'},
    ]

    # AreaSummary data
    AREA_SUMMARY_DATA = {
        'variant_count': 10,
    }

    # Extraction options data
    EXTRACTION_OPTIONS_DATA = {
        'number': 3,
    }
