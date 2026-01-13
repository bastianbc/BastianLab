# tests/unit/account/test_serializers.py
"""
Account Serializer Test Cases - No Database Required
"""
import pytest
from unittest.mock import Mock, MagicMock
from tests.utils.base_test import BaseAPITestNoDatabase
from tests.fixtures.account_fixtures import AccountTestData


class TestAccountSerializer(BaseAPITestNoDatabase):
    """Test AccountSerializer"""

    def setUp(self):
        """Set up test fixtures"""
        super().setUp()
        # Create mock user for serialization
        self.mock_user = self.create_mock_account_user()

    def create_mock_account_user(self, **kwargs):
        """Create a mock user for account serialization"""
        user = Mock()
        user.id = kwargs.get('id', 1)
        user.username = kwargs.get('username', 'testuser')
        user.first_name = kwargs.get('first_name', 'Test')
        user.last_name = kwargs.get('last_name', 'User')
        user.last_login = kwargs.get('last_login', None)

        # Mock groups
        mock_group = Mock()
        mock_group.name = kwargs.get('group_name', 'Technicians')
        user.groups = Mock()
        user.groups.first.return_value = mock_group if kwargs.get('has_group', True) else None

        return user

    def test_serializer_initialization(self):
        """Test AccountSerializer initializes correctly"""
        from account.serializers import AccountSerializer

        serializer = AccountSerializer(instance=self.mock_user)

        # Verify serializer initializes
        assert serializer is not None

    def test_serializer_contains_expected_fields(self):
        """Test serializer contains all expected fields"""
        from account.serializers import AccountSerializer

        serializer = AccountSerializer(instance=self.mock_user)
        data = serializer.data

        # Check all expected fields are present
        expected_fields = ['id', 'username', 'first_name', 'last_name', 'group', 'last_login']
        for field in expected_fields:
            assert field in data

    def test_serializer_field_count(self):
        """Test serializer has exactly the expected number of fields"""
        from account.serializers import AccountSerializer

        serializer = AccountSerializer(instance=self.mock_user)
        data = serializer.data

        # Should have 6 fields
        assert len(data) == 6

    def test_serializer_id_field(self):
        """Test id field is serialized correctly"""
        from account.serializers import AccountSerializer

        mock_user = self.create_mock_account_user(id=42)
        serializer = AccountSerializer(instance=mock_user)
        data = serializer.data

        assert data['id'] == 42

    def test_serializer_username_field(self):
        """Test username field is serialized correctly"""
        from account.serializers import AccountSerializer

        mock_user = self.create_mock_account_user(username='johndoe')
        serializer = AccountSerializer(instance=mock_user)
        data = serializer.data

        assert data['username'] == 'johndoe'

    def test_serializer_first_name_field(self):
        """Test first_name field is serialized correctly"""
        from account.serializers import AccountSerializer

        mock_user = self.create_mock_account_user(first_name='John')
        serializer = AccountSerializer(instance=mock_user)
        data = serializer.data

        assert data['first_name'] == 'John'

    def test_serializer_last_name_field(self):
        """Test last_name field is serialized correctly"""
        from account.serializers import AccountSerializer

        mock_user = self.create_mock_account_user(last_name='Doe')
        serializer = AccountSerializer(instance=mock_user)
        data = serializer.data

        assert data['last_name'] == 'Doe'

    def test_get_group_returns_group_name(self):
        """Test get_group returns the first group name"""
        from account.serializers import AccountSerializer

        mock_user = self.create_mock_account_user(group_name='Researchers', has_group=True)
        serializer = AccountSerializer(instance=mock_user)
        data = serializer.data

        assert data['group'] == 'Researchers'

    def test_get_group_returns_empty_when_no_groups(self):
        """Test get_group returns empty string when user has no groups"""
        from account.serializers import AccountSerializer

        mock_user = self.create_mock_account_user(has_group=False)
        serializer = AccountSerializer(instance=mock_user)
        data = serializer.data

        assert data['group'] == ''

    def test_get_group_method_exists(self):
        """Test get_group method exists on serializer"""
        from account.serializers import AccountSerializer

        serializer = AccountSerializer(instance=self.mock_user)

        # Verify method exists
        assert hasattr(serializer, 'get_group')
        assert callable(serializer.get_group)

    def test_serializer_meta_model(self):
        """Test Meta.model is User"""
        from account.serializers import AccountSerializer
        from account.models import User

        assert AccountSerializer.Meta.model == User

    def test_serializer_meta_fields(self):
        """Test Meta.fields includes all expected fields"""
        from account.serializers import AccountSerializer

        expected_fields = ('id', 'username', 'first_name', 'last_name', 'group', 'last_login')
        assert AccountSerializer.Meta.fields == expected_fields

    def test_serializer_group_is_method_field(self):
        """Test group field is a SerializerMethodField"""
        from account.serializers import AccountSerializer
        from rest_framework import serializers

        # Check field type
        serializer = AccountSerializer()
        assert isinstance(serializer.fields['group'], serializers.SerializerMethodField)

    def test_serializer_last_login_field(self):
        """Test last_login field is serialized correctly"""
        from account.serializers import AccountSerializer
        from datetime import datetime

        last_login = datetime(2024, 1, 1, 10, 0, 0)
        mock_user = self.create_mock_account_user(last_login=last_login)
        serializer = AccountSerializer(instance=mock_user)
        data = serializer.data

        # DateTime is serialized to ISO 8601 string
        assert data['last_login'] == '2024-01-01T10:00:00'

    def test_serializer_last_login_none(self):
        """Test last_login field handles None value"""
        from account.serializers import AccountSerializer

        mock_user = self.create_mock_account_user(last_login=None)
        serializer = AccountSerializer(instance=mock_user)
        data = serializer.data

        assert data['last_login'] is None


class TestAccountSerializerMultipleInstances(BaseAPITestNoDatabase):
    """Test AccountSerializer with multiple instances"""

    def test_serializer_many_true(self):
        """Test serializer with many=True handles multiple instances"""
        from account.serializers import AccountSerializer

        # Create multiple mock users
        mock_users = [
            Mock(
                id=1,
                username='user1',
                first_name='User',
                last_name='One',
                last_login=None,
                groups=Mock(first=Mock(return_value=Mock(name='Group1')))
            ),
            Mock(
                id=2,
                username='user2',
                first_name='User',
                last_name='Two',
                last_login=None,
                groups=Mock(first=Mock(return_value=Mock(name='Group2')))
            ),
        ]

        serializer = AccountSerializer(mock_users, many=True)
        data = serializer.data

        # Verify we got data for both users
        assert len(data) == 2
        assert data[0]['username'] == 'user1'
        assert data[1]['username'] == 'user2'

    def test_serializer_empty_list(self):
        """Test serializer handles empty list"""
        from account.serializers import AccountSerializer

        serializer = AccountSerializer([], many=True)
        data = serializer.data

        # Should return empty list
        assert data == []


class TestAccountSerializerInheritance(BaseAPITestNoDatabase):
    """Test AccountSerializer inheritance"""

    def test_serializer_inherits_from_model_serializer(self):
        """Test AccountSerializer inherits from ModelSerializer"""
        from account.serializers import AccountSerializer
        from rest_framework import serializers

        assert issubclass(AccountSerializer, serializers.ModelSerializer)


class TestAccountSerializerEdgeCases(BaseAPITestNoDatabase):
    """Test edge cases for AccountSerializer"""

    def test_serializer_with_special_characters_in_name(self):
        """Test serializer handles special characters in names"""
        from account.serializers import AccountSerializer

        user = Mock()
        user.id = 1
        user.username = 'test.user-123'
        user.first_name = "O'Brien"
        user.last_name = 'Smith-Jones'
        user.last_login = None

        # Create mock group with name attribute
        mock_group = Mock()
        mock_group.name = 'Test Group'
        user.groups = Mock()
        user.groups.first.return_value = mock_group

        serializer = AccountSerializer(instance=user)
        data = serializer.data

        assert data['username'] == 'test.user-123'
        assert data['first_name'] == "O'Brien"
        assert data['last_name'] == 'Smith-Jones'
        assert data['group'] == 'Test Group'

    def test_serializer_with_long_strings(self):
        """Test serializer handles long strings"""
        from account.serializers import AccountSerializer

        long_name = 'A' * 150
        user = Mock()
        user.id = 1
        user.username = 'testuser'
        user.first_name = long_name
        user.last_name = long_name
        user.last_login = None
        user.groups = Mock()
        user.groups.first.return_value = None

        serializer = AccountSerializer(instance=user)
        data = serializer.data

        assert data['first_name'] == long_name
        assert data['last_name'] == long_name

    def test_serializer_with_empty_strings(self):
        """Test serializer handles empty strings"""
        from account.serializers import AccountSerializer

        user = Mock()
        user.id = 1
        user.username = ''
        user.first_name = ''
        user.last_name = ''
        user.last_login = None
        user.groups = Mock()
        user.groups.first.return_value = None

        serializer = AccountSerializer(instance=user)
        data = serializer.data

        assert data['username'] == ''
        assert data['first_name'] == ''
        assert data['last_name'] == ''
        assert data['group'] == ''
