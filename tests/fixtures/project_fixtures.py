# tests/fixtures/project_fixtures.py
"""
Shared test data to ensure consistency across all test layers
"""
from datetime import datetime


class ProjectTestData:
    """Centralized test data for Projects"""

    # Valid project data that should work across all layers
    VALID_PROJECT_DATA = {
        'name': 'Test Project',
        'abbreviation': 'TP',
        'description': 'Test description',
        'speedtype': 'ST123',
        'pi': 'BB',
        'date_start': '2024-01-01',
    }

    # Sample projects matching your actual data from the screenshot
    SAMPLE_PROJECTS = [
        {
            'id': 1,
            'abbreviation': 'T/B-CR',
            'name': 'T- and B-cell Receptor Sequencing',
            'pi': 'BB',
            'pi_label': 'Boris Bastian',
            'date_start': '2025-12-10T00:00:00Z',
            'speedtype': '',
            'num_blocks': 2,
            'DT_RowId': 1,
        },
        {
            'id': 2,
            'abbreviation': 'TST',
            'name': 'TEST Project',
            'pi': 'BB',
            'pi_label': 'Boris Bastian',
            'date_start': '2025-09-16T00:00:00Z',
            'speedtype': 'MDETEST01',
            'num_blocks': 5,
            'DT_RowId': 2,
        },
        {
            'id': 3,
            'abbreviation': 'MNSC',
            'name': 'Melanocytoma-Nevus Single Cell',
            'pi': 'BB',
            'pi_label': 'Boris Bastian',
            'date_start': '2025-08-20T00:00:00Z',
            'speedtype': 'MDESHAIN20',
            'num_blocks': 0,
            'DT_RowId': 3,
        },
        {
            'id': 4,
            'abbreviation': 'AMJNCI',
            'name': 'Acral Melanoma - JNCI',
            'pi': 'BB',
            'pi_label': 'Boris Bastian',
            'date_start': '2025-08-20T00:00:00Z',
            'speedtype': '',
            'num_blocks': 76,
            'DT_RowId': 4,
        },
        {
            'id': 5,
            'abbreviation': 'MUMCL',
            'name': 'Mucosal Melanoma Cell Lines',
            'pi': 'BB',
            'pi_label': 'Boris Bastian',
            'date_start': '2025-08-20T00:00:00Z',
            'speedtype': 'MDEYEH11',
            'num_blocks': 7,
            'DT_RowId': 5,
        },
        {
            'id': 6,
            'abbreviation': 'XCL',
            'name': 'Xu Cell Lines',
            'pi': 'BB',
            'pi_label': 'Boris Bastian',
            'date_start': '2025-08-19T00:00:00Z',
            'speedtype': '',
            'num_blocks': 64,
            'DT_RowId': 6,
        },
        {
            'id': 7,
            'abbreviation': 'Met',
            'name': 'Met Fusions',
            'pi': 'BB',
            'pi_label': 'Boris Bastian',
            'date_start': '2025-06-10T00:00:00Z',
            'speedtype': '',
            'num_blocks': 8,
            'DT_RowId': 7,
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
        'date_range': [''],
        'pi': [''],
        'technician': [''],
        'researcher': [''],
    }

    # Editor AJAX format (what JS sends for inline editing)
    EDITOR_REQUEST_DATA = {
        'data': {
            '1': {
                'abbreviation': 'TP',
                'name': 'Updated Project',
                'pi': 'BB',
                'date_start': '2024-01-01',
                'speedtype': 'ST123',
            }
        }
    }

    # Expected response format (what views should return)
    DATATABLES_RESPONSE = {
        'draw': 1,
        'recordsTotal': 7,
        'recordsFiltered': 7,
        'data': SAMPLE_PROJECTS  # Use sample projects as data
    }

    # Expected DataTables response with all fields (matching serializer)
    @staticmethod
    def get_datatables_response_with_projects():
        """Returns a complete DataTables response with sample projects"""
        return {
            'draw': 1,
            'recordsTotal': len(ProjectTestData.SAMPLE_PROJECTS),
            'recordsFiltered': len(ProjectTestData.SAMPLE_PROJECTS),
            'data': ProjectTestData.SAMPLE_PROJECTS
        }

    # Single project for testing (matching your TST project)
    SINGLE_PROJECT = {
        'id': 2,
        'abbreviation': 'TST',
        'name': 'TEST Project',
        'pi': 'BB',
        'pi_label': 'Boris Bastian',
        'date_start': '2025-09-16T00:00:00Z',
        'speedtype': 'MDETEST01',
        'num_blocks': 5,
        'DT_RowId': 2,
    }

    # Project with no blocks
    PROJECT_NO_BLOCKS = {
        'id': 3,
        'abbreviation': 'MNSC',
        'name': 'Melanocytoma-Nevus Single Cell',
        'pi': 'BB',
        'pi_label': 'Boris Bastian',
        'date_start': '2025-08-20T00:00:00Z',
        'speedtype': 'MDESHAIN20',
        'num_blocks': 0,
        'DT_RowId': 3,
    }

    # Project with many blocks
    PROJECT_MANY_BLOCKS = {
        'id': 4,
        'abbreviation': 'AMJNCI',
        'name': 'Acral Melanoma - JNCI',
        'pi': 'BB',
        'pi_label': 'Boris Bastian',
        'date_start': '2025-08-20T00:00:00Z',
        'speedtype': '',
        'num_blocks': 76,
        'DT_RowId': 4,
    }