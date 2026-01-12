# tests/settings.py
"""
Test settings - Imports production settings and overrides for testing

This is 100% safe - uses in-memory SQLite database that is destroyed after tests.
Your production database is never touched.
"""

# Import ALL settings from your production settings
from test1.settings import *

# Override ONLY what's needed for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # Database exists only in RAM, deleted after tests
    }
}


# Disable migrations for faster test execution
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = DisableMigrations()

# Use faster (less secure) password hasher for tests only
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Optional: Make tests even faster
DEBUG = False  # Faster without debug
LOGGING_CONFIG = None  # Disable logging in tests

# Optional: Disable unnecessary middleware for tests
MIDDLEWARE = [m for m in MIDDLEWARE if 'SecurityMiddleware' not in m]