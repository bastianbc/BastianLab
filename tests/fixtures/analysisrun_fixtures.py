# tests/fixtures/analysisrun_fixtures.py
"""
Centralized test data for Analysisrun operations
"""
from datetime import datetime


class AnalysisrunTestData:
    """Centralized test data for Analysisrun operations"""

    SAMPLE_ANALYSIS_RUN = {
        'id': 1,
        'name': 'AR1',
        'pipeline': 'dna-v1',
        'genome': 'hg38',
        'date': datetime.now(),
        'sheet': 'AR1_dna-v1_hg38.csv',
        'sheet_name': 'AR1_dna-v1_hg38',
        'status': 'pending',
    }

    SAMPLE_ANALYSIS_RUNS = [
        {
            'id': 1,
            'name': 'AR1',
            'pipeline': 'dna-v1',
            'genome': 'hg38',
            'date': datetime.now(),
            'status': 'pending',
        },
        {
            'id': 2,
            'name': 'AR2',
            'pipeline': 'dna-v1',
            'genome': 'hg19',
            'date': datetime.now(),
            'status': 'processing',
        },
        {
            'id': 3,
            'name': 'AR3',
            'pipeline': 'dna-v1',
            'genome': 'hg38',
            'date': datetime.now(),
            'status': 'imported',
        },
    ]

    SAMPLE_VARIANT_FILE = {
        'id': 1,
        'type': 'variant',
        'name': 'sample_FB.vcf',
        'directory': '/path/to/variants/',
        'date': datetime.now(),
        'call': False,
        'status': 'pending',
    }

    DATATABLES_REQUEST = {
        'draw': ['1'],
        'start': ['0'],
        'length': ['10'],
        'search[value]': [''],
        'order[0][column]': ['0'],
        'order[0][dir]': ['asc'],
    }

    ANALYSIS_RUN_FORM_DATA = {
        'pipeline': 'dna-v1',
        'genome': 'hg38',
    }
