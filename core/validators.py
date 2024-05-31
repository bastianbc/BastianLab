from django.core.exceptions import ValidationError

def validate_name_contains_space(value):
    if ' ' in value:
        raise ValidationError(
            'The name field must not contain spaces.',
            params={'value': value},
        )
