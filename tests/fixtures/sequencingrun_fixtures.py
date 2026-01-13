# tests/fixtures/sequencingrun_fixtures.py
"""
Sequencingrun Test Data Fixtures
"""
from datetime import datetime


class SequencingrunTestData:
    """Centralized test data for Sequencingrun operations"""

    SAMPLE_SEQUENCINGRUN = {
        'id': 1,
        'name': 'SR-001',
        'date_run': datetime.now(),
        'date': datetime.now(),
        'facility': 'cat',
        'sequencer': 'novaseq-6000-s4',
        'pe': 'PE 150',
        'amp_cycles': 12,
        'notes': 'Test sequencing run',
    }

    SAMPLE_SEQUENCINGRUNS = [
        {
            'id': 1,
            'name': 'SR-001',
            'date_run': datetime.now(),
            'date': datetime.now(),
            'facility': 'cat',
            'sequencer': 'novaseq-6000-s4',
            'pe': 'PE 150',
            'amp_cycles': 12,
        },
        {
            'id': 2,
            'name': 'SR-002',
            'date_run': datetime.now(),
            'date': datetime.now(),
            'facility': 'ihg',
            'sequencer': 'novaseq-6000-s2',
            'pe': 'PE 100',
            'amp_cycles': 10,
        },
        {
            'id': 3,
            'name': 'SR-003',
            'date_run': datetime.now(),
            'date': datetime.now(),
            'facility': 'broad-institute',
            'sequencer': 'hiseq-2500',
            'pe': 'PE 50',
            'amp_cycles': 14,
        },
    ]

    DATATABLES_REQUEST = {
        'draw': ['1'],
        'length': ['10'],
        'start': ['0'],
        'search[value]': [''],
        'order[0][column]': ['1'],
        'order[0][dir]': ['asc'],
    }

    SEQUENCINGRUN_FORM_DATA = {
        'name': 'SR-Test-001',
        'date_run': '2024-01-15 10:00:00',
        'date': '2024-01-15',
        'facility': 'cat',
        'sequencer': 'novaseq-6000-s4',
        'pe': 'PE 150',
        'amp_cycles': 12,
        'notes': 'Test notes',
    }

    SEQUENCINGRUN_CREATION_FORM_DATA = {
        'prefix': 'SR',
        'date_run': '2024-01-15 10:00:00',
        'date': '2024-01-15',
        'facility': 'cat',
        'sequencer': 'novaseq-6000-s4',
        'pe': 'PE 150',
        'amp_cycles': 12,
    }
