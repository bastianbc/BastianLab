# tests/fixtures/account_fixtures.py
"""
Shared test data for account/authentication testing
"""
from datetime import datetime, timedelta


class AccountTestData:
    """Centralized test data for Account operations"""

    # Valid user creation data
    VALID_USER_DATA = {
        'username': 'testuser',
        'password': 'SecurePass123!',
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'test@example.com',
    }

    # User data for CreateAccountForm
    CREATE_ACCOUNT_DATA = {
        'username': 'newuser',
        'password': 'NewPass123!',
        'first_name': 'New',
        'last_name': 'User',
        'groups': [],  # Will be set in tests
    }

    # User data for EditAccountForm
    EDIT_ACCOUNT_DATA = {
        'username': 'editeduser',
        'first_name': 'Edited',
        'last_name': 'User',
        'groups': [],
    }

    # Login form data
    LOGIN_DATA = {
        'username': 'testuser',
        'password': 'testpass123',
    }

    # Invalid login data
    INVALID_LOGIN_DATA = {
        'username': 'wronguser',
        'password': 'wrongpass',
    }

    # Password reset request data
    PASSWORD_RESET_REQUEST_DATA = {
        'email': 'test@example.com',
    }

    # Set new password data
    SET_PASSWORD_DATA = {
        'new_password1': 'NewSecurePass123!',
        'new_password2': 'NewSecurePass123!',
    }

    # Mismatched passwords
    MISMATCHED_PASSWORD_DATA = {
        'new_password1': 'NewSecurePass123!',
        'new_password2': 'DifferentPass123!',
    }

    # DataTables request format (for filter_accounts)
    DATATABLES_REQUEST = {
        'draw': ['1'],
        'length': ['10'],
        'start': ['0'],
        'search[value]': [''],
        'order[0][column]': ['0'],
        'order[0][dir]': ['asc'],
    }

    # Sample users for DataTables response
    SAMPLE_USERS = [
        {
            'id': 1,
            'username': 'user1',
            'first_name': 'John',
            'last_name': 'Doe',
            'group': 'Technicians',
            'last_login': '2024-01-01T10:00:00Z',
        },
        {
            'id': 2,
            'username': 'user2',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'group': 'Researchers',
            'last_login': '2024-01-02T11:00:00Z',
        },
        {
            'id': 3,
            'username': 'user3',
            'first_name': 'Bob',
            'last_name': 'Johnson',
            'group': 'Primary Investigators',
            'last_login': None,
        },
    ]

    # Expected DataTables response
    DATATABLES_RESPONSE = {
        'draw': 1,
        'recordsTotal': 3,
        'recordsFiltered': 3,
        'data': SAMPLE_USERS
    }