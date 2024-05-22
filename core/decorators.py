from django.http import HttpResponseForbidden
from functools import wraps

def permission_required_for_async(permission):
    def decorator(function):
        @wraps(function)
        def wrapper(request, *args, **kwargs):
            if request.user.has_perm(permission):
                return function(request, *args, **kwargs)
            else:
                return HttpResponseForbidden()
        return wrapper
    return decorator
