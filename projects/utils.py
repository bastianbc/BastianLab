from .models import Project
from django.db.models import Q

def get_user_projects(user):
    """
    Returns a queryset of projects that the user has access to
    """
    return Project.objects.filter(
        Q(researcher=user) | Q(technician=user) | Q(primary_investigator=user)
    ).distinct()
