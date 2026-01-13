# tests/unit/authentication/test_forms.py
"""
Authentication Forms Test Cases - No Database Required
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django import forms
from tests.utils.base_test import BaseAPITestNoDatabase
from tests.fixtures.authentication_fixtures import AuthenticationTestData


class TestLoginForm(BaseAPITestNoDatabase):
    """Test LoginForm"""

    def test_form_initialization(self):
        """Test LoginForm initializes correctly"""
        from authentication.forms import LoginForm
        form = LoginForm()

        # Verify form initializes successfully
        assert form is not None
        assert 'username' in form.fields
        assert 'password' in form.fields

    def test_form_has_all_fields(self):
        """Test form contains all expected fields"""
        from authentication.forms import LoginForm
        form = LoginForm()

        # Verify all fields are present
        expected_fields = ['username', 'password']
        for field_name in expected_fields:
            assert field_name in form.fields

    def test_form_meta_model(self):
        """Test form Meta.model is User"""
        from authentication.forms import LoginForm
        from account.models import User

        assert LoginForm.Meta.model == User

    def test_form_meta_fields(self):
        """Test form Meta.fields includes all expected fields"""
        from authentication.forms import LoginForm

        expected_fields = ['username', 'password']
        assert LoginForm.Meta.fields == expected_fields

    def test_password_widget_is_password_input(self):
        """Test password field uses PasswordInput widget"""
        from authentication.forms import LoginForm
        form = LoginForm()

        # Verify password widget
        assert isinstance(form.fields['password'].widget, forms.PasswordInput)

    def test_form_inherits_from_base_form(self):
        """Test LoginForm inherits from BaseForm"""
        from authentication.forms import LoginForm
        from core.forms import BaseForm

        assert issubclass(LoginForm, BaseForm)

    def test_username_field_widget_attrs(self):
        """Test username field has correct widget attributes"""
        from authentication.forms import LoginForm
        form = LoginForm()

        # Check widget attributes
        assert 'bg-transparent' in form.fields['username'].widget.attrs.get('class', '')
        assert form.fields['username'].widget.attrs.get('placeholder') == 'Username'

    def test_password_field_widget_attrs(self):
        """Test password field has correct widget attributes"""
        from authentication.forms import LoginForm
        form = LoginForm()

        # Check widget attributes
        assert 'bg-transparent' in form.fields['password'].widget.attrs.get('class', '')
        assert form.fields['password'].widget.attrs.get('placeholder') == 'Password'

    def test_form_field_count(self):
        """Test LoginForm has exactly the expected number of fields"""
        from authentication.forms import LoginForm
        form = LoginForm()

        # Should have 2 fields
        assert len(form.fields) == 2


class TestPasswordResetRequestForm(BaseAPITestNoDatabase):
    """Test PasswordResetRequestForm"""

    def test_form_initialization(self):
        """Test PasswordResetRequestForm initializes correctly"""
        from authentication.forms import PasswordResetRequestForm
        form = PasswordResetRequestForm()

        # Form should initialize successfully
        assert form is not None
        assert 'email' in form.fields

    def test_form_has_email_field(self):
        """Test form has email field"""
        from authentication.forms import PasswordResetRequestForm
        form = PasswordResetRequestForm()

        assert 'email' in form.fields

    def test_email_field_is_email_field(self):
        """Test email field is EmailField"""
        from authentication.forms import PasswordResetRequestForm
        form = PasswordResetRequestForm()

        assert isinstance(form.fields['email'], forms.EmailField)

    def test_email_field_max_length(self):
        """Test email field has correct max_length"""
        from authentication.forms import PasswordResetRequestForm
        form = PasswordResetRequestForm()

        assert form.fields['email'].max_length == 254

    def test_email_field_widget_attrs(self):
        """Test email field has correct widget attributes"""
        from authentication.forms import PasswordResetRequestForm
        form = PasswordResetRequestForm()

        attrs = form.fields['email'].widget.attrs
        assert 'form-control' in attrs.get('class', '')
        assert 'bg-transparent' in attrs.get('class', '')
        assert attrs.get('placeholder') == 'Email Address'
        assert attrs.get('autocomplete') == 'email'

    def test_form_inherits_from_forms_form(self):
        """Test PasswordResetRequestForm inherits from forms.Form"""
        from authentication.forms import PasswordResetRequestForm

        assert issubclass(PasswordResetRequestForm, forms.Form)

    def test_form_field_count(self):
        """Test PasswordResetRequestForm has exactly 1 field"""
        from authentication.forms import PasswordResetRequestForm
        form = PasswordResetRequestForm()

        # Should have 1 field
        assert len(form.fields) == 1

    @patch('authentication.forms.User.objects')
    def test_clean_email_with_valid_email(self, mock_user_objects):
        """Test clean_email with valid email that exists"""
        from authentication.forms import PasswordResetRequestForm

        # Mock that user exists
        mock_user_objects.filter.return_value.exists.return_value = True

        form = PasswordResetRequestForm(data={'email': 'test@example.com'})

        # Trigger validation
        is_valid = form.is_valid()

        # Should be valid
        assert is_valid is True

    @patch('authentication.forms.User.objects')
    def test_clean_email_with_nonexistent_email(self, mock_user_objects):
        """Test clean_email raises error for nonexistent email"""
        from authentication.forms import PasswordResetRequestForm

        # Mock that user doesn't exist
        mock_user_objects.filter.return_value.exists.return_value = False

        form = PasswordResetRequestForm(data={'email': 'nonexistent@example.com'})

        # Trigger validation
        is_valid = form.is_valid()

        # Should be invalid
        assert is_valid is False
        assert 'email' in form.errors


class TestSetNewPasswordForm(BaseAPITestNoDatabase):
    """Test SetNewPasswordForm"""

    def test_form_initialization(self):
        """Test SetNewPasswordForm initializes correctly"""
        from authentication.forms import SetNewPasswordForm
        form = SetNewPasswordForm()

        # Form should initialize successfully
        assert form is not None

    def test_form_has_all_fields(self):
        """Test form has all expected fields"""
        from authentication.forms import SetNewPasswordForm
        form = SetNewPasswordForm()

        assert 'new_password1' in form.fields
        assert 'new_password2' in form.fields

    def test_password_fields_are_password_input(self):
        """Test password fields use PasswordInput widget"""
        from authentication.forms import SetNewPasswordForm
        form = SetNewPasswordForm()

        assert isinstance(form.fields['new_password1'].widget, forms.PasswordInput)
        assert isinstance(form.fields['new_password2'].widget, forms.PasswordInput)

    def test_new_password1_field_widget_attrs(self):
        """Test new_password1 field has correct widget attributes"""
        from authentication.forms import SetNewPasswordForm
        form = SetNewPasswordForm()

        attrs = form.fields['new_password1'].widget.attrs
        assert 'form-control' in attrs.get('class', '')
        assert 'bg-transparent' in attrs.get('class', '')
        assert attrs.get('placeholder') == 'New Password'
        assert attrs.get('autocomplete') == 'new-password'

    def test_new_password2_field_widget_attrs(self):
        """Test new_password2 field has correct widget attributes"""
        from authentication.forms import SetNewPasswordForm
        form = SetNewPasswordForm()

        attrs = form.fields['new_password2'].widget.attrs
        assert 'form-control' in attrs.get('class', '')
        assert 'bg-transparent' in attrs.get('class', '')
        assert attrs.get('placeholder') == 'Confirm New Password'
        assert attrs.get('autocomplete') == 'new-password'

    def test_form_inherits_from_forms_form(self):
        """Test SetNewPasswordForm inherits from forms.Form"""
        from authentication.forms import SetNewPasswordForm

        assert issubclass(SetNewPasswordForm, forms.Form)

    def test_form_field_count(self):
        """Test SetNewPasswordForm has exactly 2 fields"""
        from authentication.forms import SetNewPasswordForm
        form = SetNewPasswordForm()

        # Should have 2 fields
        assert len(form.fields) == 2

    def test_clean_new_password2_matching_passwords(self):
        """Test clean_new_password2 with matching passwords"""
        from authentication.forms import SetNewPasswordForm

        data = {
            'new_password1': 'SecurePass123!',
            'new_password2': 'SecurePass123!',
        }
        form = SetNewPasswordForm(data=data)

        # Should be valid
        assert form.is_valid() is True

    def test_clean_new_password2_mismatched_passwords(self):
        """Test clean_new_password2 raises error for mismatched passwords"""
        from authentication.forms import SetNewPasswordForm

        data = {
            'new_password1': 'SecurePass123!',
            'new_password2': 'DifferentPass123!',
        }
        form = SetNewPasswordForm(data=data)

        # Should be invalid
        assert form.is_valid() is False
        assert 'new_password2' in form.errors

    def test_new_password1_field_label(self):
        """Test new_password1 field has correct label"""
        from authentication.forms import SetNewPasswordForm
        form = SetNewPasswordForm()

        assert form.fields['new_password1'].label == 'New password'

    def test_new_password2_field_label(self):
        """Test new_password2 field has correct label"""
        from authentication.forms import SetNewPasswordForm
        form = SetNewPasswordForm()

        assert form.fields['new_password2'].label == 'Confirm password'

    def test_password_fields_strip_false(self):
        """Test password fields have strip=False"""
        from authentication.forms import SetNewPasswordForm
        form = SetNewPasswordForm()

        # strip=False means whitespace is preserved
        assert form.fields['new_password1'].strip is False
        assert form.fields['new_password2'].strip is False


class TestFormIntegration(BaseAPITestNoDatabase):
    """Integration tests for forms"""

    def test_login_form_with_data(self):
        """Test LoginForm with valid data"""
        from authentication.forms import LoginForm

        data = {
            'username': 'testuser',
            'password': 'testpass123',
        }

        form = LoginForm(data=data)

        # Form should be instantiated
        assert form is not None

    @patch('authentication.forms.User.objects')
    def test_password_reset_request_form_with_data(self, mock_user_objects):
        """Test PasswordResetRequestForm with valid data"""
        from authentication.forms import PasswordResetRequestForm

        # Mock user exists
        mock_user_objects.filter.return_value.exists.return_value = True

        data = {
            'email': 'test@example.com',
        }

        form = PasswordResetRequestForm(data=data)

        # Form should be valid
        assert form.is_valid() is True

    def test_set_new_password_form_with_data(self):
        """Test SetNewPasswordForm with valid data"""
        from authentication.forms import SetNewPasswordForm

        data = {
            'new_password1': 'NewSecurePass123!',
            'new_password2': 'NewSecurePass123!',
        }

        form = SetNewPasswordForm(data=data)

        # Form should be valid
        assert form.is_valid() is True
