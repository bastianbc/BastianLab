# tests/utils/auth_utils.py
"""
Authentication and Permission Test Utilities for Account App

Provides reusable functions for creating users, groups, and permissions
based on the actual account.models.User implementation.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

User = get_user_model()


class PermissionFactory:
    """Factory for creating permissions in tests"""

    @staticmethod
    def create_permission(codename, name, app_label='account', model='user'):
        """
        Create a permission

        Args:
            codename (str): Permission codename (e.g., 'view_user')
            name (str): Permission name (e.g., 'Can view user')
            app_label (str): App label
            model (str): Model name

        Returns:
            Permission: Created permission object
        """
        content_type, _ = ContentType.objects.get_or_create(
            app_label=app_label,
            model=model
        )

        permission, created = Permission.objects.get_or_create(
            codename=codename,
            name=name,
            content_type=content_type,
        )
        return permission

    @staticmethod
    def create_account_permissions():
        """
        Create all account permissions

        Returns:
            dict: Dictionary of permissions keyed by action
        """
        permissions = {
            'view': PermissionFactory.create_permission(
                'view_user',
                'Can view user',
                app_label='account'
            ),
            'add': PermissionFactory.create_permission(
                'add_user',
                'Can add user',
                app_label='account'
            ),
            'change': PermissionFactory.create_permission(
                'change_user',
                'Can change user',
                app_label='account'
            ),
            'delete': PermissionFactory.create_permission(
                'delete_user',
                'Can delete user',
                app_label='account'
            ),
        }
        return permissions

    @staticmethod
    def create_all_permissions_except_delete():
        """
        Create all permissions except delete permissions
        (matching CreateAccountForm behavior)

        Returns:
            QuerySet: Permissions excluding delete permissions
        """
        # Create all permissions first
        PermissionFactory.create_account_permissions()

        # Return all except delete
        return Permission.objects.filter(~Q(codename__contains='delete'))


class GroupFactory:
    """Factory for creating user groups in tests"""

    @staticmethod
    def create_group(name, permissions=None):
        """
        Create a user group with optional permissions

        Args:
            name (str): Group name
            permissions (list): List of Permission objects

        Returns:
            Group: Created group object
        """
        group, created = Group.objects.get_or_create(name=name)

        if permissions:
            group.permissions.set(permissions)

        return group

    @staticmethod
    def create_technician_group():
        """Create Technicians group"""
        return GroupFactory.create_group('Technicians')

    @staticmethod
    def create_researcher_group():
        """Create Researchers group"""
        return GroupFactory.create_group('Researchers')

    @staticmethod
    def create_pi_group():
        """Create Primary Investigators group"""
        return GroupFactory.create_group('Primary Investigators')

    @staticmethod
    def create_all_groups():
        """
        Create all standard groups

        Returns:
            dict: Dictionary of groups keyed by role
        """
        groups = {
            'technician': GroupFactory.create_technician_group(),
            'researcher': GroupFactory.create_researcher_group(),
            'pi': GroupFactory.create_pi_group(),
        }
        return groups


class UserFactory:
    """Factory for creating test users"""

    @staticmethod
    def create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            is_staff=False,
            is_superuser=False,
            **extra_fields
    ):
        """
        Create a basic user

        Args:
            username (str): Username
            password (str): Password
            email (str): Email address
            first_name (str): First name
            last_name (str): Last name
            is_staff (bool): Staff status
            is_superuser (bool): Superuser status
            **extra_fields: Additional user fields

        Returns:
            User: Created user object
        """
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_staff=is_staff,
            is_superuser=is_superuser,
            **extra_fields
        )
        return user

    @staticmethod
    def create_user_without_password(
            username='newuser',
            email='new@example.com',
            first_name='New',
            last_name='User',
            **extra_fields
    ):
        """
        Create user without password (for first login flow)
        Sets last_login to None to trigger set_password flow

        Returns:
            User: User object without password set
        """
        user = User.objects.create(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            last_login=None,
            **extra_fields
        )
        return user

    @staticmethod
    def create_user_with_permissions(
            username='testuser',
            password='testpass123',
            permissions=None,
            **extra_fields
    ):
        """
        Create user with specific permissions

        Args:
            username (str): Username
            password (str): Password
            permissions (list): List of Permission objects
            **extra_fields: Additional user fields

        Returns:
            User: Created user with permissions
        """
        user = UserFactory.create_user(
            username=username,
            password=password,
            **extra_fields
        )

        if permissions:
            user.user_permissions.set(permissions)

        return user

    @staticmethod
    def create_user_with_groups(
            username='testuser',
            password='testpass123',
            groups=None,
            **extra_fields
    ):
        """
        Create user with group memberships

        Args:
            username (str): Username
            password (str): Password
            groups (list): List of Group objects
            **extra_fields: Additional user fields

        Returns:
            User: Created user with groups
        """
        user = UserFactory.create_user(
            username=username,
            password=password,
            **extra_fields
        )

        if groups:
            user.groups.set(groups)

        return user

    @staticmethod
    def create_superuser(
            username='admin',
            password='adminpass123',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            **extra_fields
    ):
        """Create a superuser"""
        return User.objects.create_superuser(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )

    @staticmethod
    def create_technician(
            username='technician',
            password='techpass123',
            first_name='Tech',
            last_name='User',
            **extra_fields
    ):
        """Create user in Technicians group"""
        group = GroupFactory.create_technician_group()
        return UserFactory.create_user_with_groups(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            groups=[group],
            **extra_fields
        )

    @staticmethod
    def create_researcher(
            username='researcher',
            password='researchpass123',
            first_name='Research',
            last_name='User',
            **extra_fields
    ):
        """Create user in Researchers group"""
        group = GroupFactory.create_researcher_group()
        return UserFactory.create_user_with_groups(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            groups=[group],
            **extra_fields
        )

    @staticmethod
    def create_pi(
            username='pi',
            password='pipass123',
            first_name='Principal',
            last_name='Investigator',
            **extra_fields
    ):
        """Create user in Primary Investigators group"""
        group = GroupFactory.create_pi_group()
        return UserFactory.create_user_with_groups(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            groups=[group],
            **extra_fields
        )