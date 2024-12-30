from .models import Project
from django.db.models import Q

def get_user_projects(user):
    """
    Returns a queryset of projects that the user has access to
    """
    from projects.models import Project  # Import here to avoid circular imports

    return Project.objects.filter(
        Q(researcher=user) | Q(technician=user)
    ).distinct()
