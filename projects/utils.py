from .models import Project
from django.db.models import Q

def get_user_projects(user):
    """
    Returns a queryset of projects that the user has access to
    """
<<<<<<< HEAD
    return Project.objects.filter(
        Q(researcher=user) | Q(technician=user) | Q(primary_investigator=user)
=======
    from projects.models import Project  # Import here to avoid circular imports

    return Project.objects.filter(
        Q(researcher=user) | Q(technician=user)
>>>>>>> f5ad8a5df330d075c2c0f5de8add74e458a8ca35
    ).distinct()
