# tests/fixtures/blocks_fixtures.py
"""
Shared test data for blocks testing
"""
from datetime import datetime


class BlocksTestData:
    """Centralized test data for Blocks operations"""

    # Sample block data
    SAMPLE_BLOCK = {
        'id': 1,
        'name': 'BLK001',
        'age': 55.5,
        'ulceration': True,
        'thickness': 2.5,
        'mitoses': 3,
        'p_stage': 'T2a',
        'csd_score': '2',
        'prim': 'primary',
        'subtype': 'low-csd',
        'slides': 10,
        'slides_left': 8,
        'fixation': 'ffpe',
        'storage': 'Room A',
        'scan_number': 'SCAN123',
        'icd10': 'C43.9',
        'diagnosis': 'Malignant melanoma',
        'notes': 'Test notes',
        'date_added': datetime(2024, 1, 1, 10, 0, 0),
        'num_areas': 3,
        'num_variants': 5,
        'patient_id': 1,
        'project_num': 2,
        'patient_num': 1,
    }

    # Sample blocks list
    SAMPLE_BLOCKS = [
        {
            'id': 1,
            'name': 'BLK001',
            'patient_id': 1,
            'project': 'PROJ1',
            'patient': 'PAT001',
            'diagnosis': 'Melanoma',
            'body_site': 'Arm',
            'thickness': 2.5,
            'date_added': '2024-01-01T10:00:00Z',
            'num_areas': 3,
            'DT_RowId': 1,
            'block_url': 'http://example.com/blocks/',
            'scan_number': 'SCAN123',
            'num_variants': '5',
        },
        {
            'id': 2,
            'name': 'BLK002',
            'patient_id': 2,
            'project': 'PROJ2',
            'patient': 'PAT002',
            'diagnosis': 'Melanoma stage 2',
            'body_site': 'Leg',
            'thickness': 1.8,
            'date_added': '2024-01-02T11:00:00Z',
            'num_areas': 2,
            'DT_RowId': 2,
            'block_url': 'http://example.com/blocks/',
            'scan_number': 'SCAN456',
            'num_variants': '3',
        },
    ]

    # DataTables request format
    DATATABLES_REQUEST = {
        'draw': ['1'],
        'length': ['10'],
        'start': ['0'],
        'search[value]': [''],
        'p_stage': [''],
        'prim': [''],
        'body_site': [''],
        'order[0][column]': ['1'],
        'order[0][dir]': ['asc'],
    }

    # P_STAGE types
    P_STAGE_TYPES = (
        ("Tis", "Tis"),
        ("T1a", "T1a"),
        ("T1b", "T1b"),
        ("T2a", "T2a"),
        ("T2b", "T2b"),
        ("T3a", "T3a"),
        ("T3b", "T3b"),
        ("T4a", "T4a"),
        ("T4b", "T4b"),
    )

    # PRIM types
    PRIM_TYPES = (
        ("primary", "Primary"),
        ("metastasis", "Metastasis"),
    )

    # SUBTYPE choices
    SUBTYPE_CHOICES = (
        ("low-csd", "Low CSD"),
        ("high-csd", "High CSD"),
        ("acral", "Acral"),
        ("mucosal", "Mucosal"),
        ("uveal", "Uveal"),
        ("desmoplastic", "Desmoplastic"),
    )

    # FIXATION choices
    FIXATION_CHOICES = (
        ("ffpe", "FFPE"),
        ("frozen", "frozen"),
        ("ethanol", "ethanol"),
    )

    # CSD choices
    CSD_CHOICES = (
        ("0", "0"),
        ("1", "1"),
        ("2", "2"),
        ("3", "3"),
    )

    # BlockUrl data
    BLOCK_URL_DATA = {
        'url': 'http://example.com/blocks/',
    }

    # BlockSummary data
    BLOCK_SUMMARY_DATA = {
        'variant_count': 10,
    }
