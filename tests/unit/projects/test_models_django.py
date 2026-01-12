# tests/integration/projects/test_models_integration.py
"""
Project Model Integration Tests - WITH Database

These tests use Django's TestCase which creates a real test database.
Use these for testing actual database operations and relationships.

Run with: pytest tests/integration/projects/test_models_integration.py -v
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import datetime
from projects.models import Project
from blocks.models import Block

User = get_user_model()


class ProjectModelIntegrationTest(TestCase):
    """Integration tests for Project model with real database"""

    def setUp(self):
        """Set up test data in database"""
        # Create test users
        self.superuser = User.objects.create_superuser(
            username='admin',
            password='adminpass',
            email='admin@test.com',
            first_name='Admin',
            last_name='User'
        )

        self.regular_user = User.objects.create_user(
            username='testuser',
            password='testpass',
            email='test@test.com',
            first_name='Test',
            last_name='User'
        )

        # Create test project
        self.project = Project.objects.create(
            name='Test Project',
            abbreviation='TST',
            pi='BB',
            speedtype='SPEED123',
            description='Test Description'
        )

    def test_create_project_and_save_to_database(self):
        """Test creating a project saves correctly to database"""
        # Create a new project
        project = Project.objects.create(
            name='Integration Test Project',
            abbreviation='ITP',
            pi='IY',
            speedtype='MDEYEH11',
            description='Integration test description'
        )

        # Verify it was saved
        assert project.id is not None
        assert project.name == 'Integration Test Project'
        assert project.abbreviation == 'ITP'
        assert project.get_pi_display() == 'Iwei Yeh'

        # Verify we can retrieve it from database
        retrieved = Project.objects.get(abbreviation='ITP')
        assert retrieved.name == 'Integration Test Project'
        assert retrieved.speedtype == 'MDEYEH11'

        # Verify __str__ method
        assert str(retrieved) == 'Integration Test Project'

        # Verify total count
        assert Project.objects.count() == 2  # setUp created 1, this test created 1

    def test_query_by_args_with_superuser_returns_all_projects(self):
        """Test query_by_args returns all projects for superuser"""
        # Create additional projects
        Project.objects.create(
            name='Project 2',
            abbreviation='PR2',
            pi='BB'
        )
        Project.objects.create(
            name='Project 3',
            abbreviation='PR3',
            pi='AH'
        )

        # Prepare DataTables request parameters
        params = {
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

        # Call query_by_args with superuser
        project = Project()
        result = project.query_by_args(self.superuser, **params)

        # Verify results
        assert result['total'] == 3  # All 3 projects
        assert result['count'] == 3  # No filtering applied
        assert result['draw'] == 1
        assert len(list(result['items'])) == 3

        # Verify num_blocks annotation exists
        first_item = list(result['items'])[0]
        assert hasattr(first_item, 'num_blocks')

    def test_project_many_to_many_relationships(self):
        """Test Project ManyToMany fields work correctly"""
        # Add users to project relationships
        self.project.technician.add(self.regular_user)
        self.project.primary_investigator.add(self.superuser)

        # Verify relationships were saved
        assert self.project.technician.count() == 1
        assert self.project.primary_investigator.count() == 1

        # Verify reverse relationships work
        assert self.regular_user.technician_projects.count() == 1
        assert self.regular_user.technician_projects.first() == self.project

        assert self.superuser.pi_projects.count() == 1
        assert self.superuser.pi_projects.first() == self.project

        # Test query_by_args filters for regular user
        params = {
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

        # Regular user should only see projects they're assigned to
        project_instance = Project()
        result = project_instance.query_by_args(self.regular_user, **params)

        # Should return 1 project (the one regular_user is technician for)
        assert result['total'] == 1
        assert result['count'] == 1
        assert list(result['items'])[0].id == self.project.id