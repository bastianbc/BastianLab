# tests/fixtures/authentication_fixtures.py
"""
Shared test data for authentication testing
"""


class AuthenticationTestData:
    """Centralized test data for Authentication operations"""

    # Valid login credentials
    VALID_LOGIN_DATA = {
        'username': 'testuser',
        'password': 'testpass123',
    }

    # Invalid login credentials
    INVALID_LOGIN_DATA = {
        'username': 'wronguser',
        'password': 'wrongpass',
    }

    # Password reset request data
    PASSWORD_RESET_REQUEST = {
        'email': 'test@example.com',
    }

    # Invalid email for password reset
    INVALID_EMAIL_RESET = {
        'email': 'nonexistent@example.com',
    }

    # Set new password data
    SET_NEW_PASSWORD_DATA = {
        'new_password1': 'NewSecurePass123!',
        'new_password2': 'NewSecurePass123!',
    }

    # Mismatched passwords
    MISMATCHED_PASSWORD_DATA = {
        'new_password1': 'NewSecurePass123!',
        'new_password2': 'DifferentPass123!',
    }

    # Change password data
    CHANGE_PASSWORD_DATA = {
        'old_password': 'oldpass123',
        'new_password1': 'NewPass123!',
        'new_password2': 'NewPass123!',
    }
