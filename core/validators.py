# These validations are run when you are trying to create an instance of a model.
# It's run on the level of database.

from django.core.exceptions import ValidationError
from datetime import datetime

def validate_name_contains_space(value):
    """
    It checks if the value given has any space characters. Space character not allowed.
    """
    if ' ' in value:
        raise ValidationError(
            'The name field must not contain spaces.',
            params={'value': value},
        )

def validate_birthyear_range(value):
    """
    It checks if the value given is between 1900 and current year.
    """
    now = datetime.now()
    if value < 1900 or value > now.year:
        raise ValidationError(
            'The name field must not contain spaces.',
            params={'value': value},
        )
