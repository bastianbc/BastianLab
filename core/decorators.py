from django.http import HttpResponseForbidden
from functools import wraps

def permission_required_for_async(perm):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            print("perm:",perm)
            if request.user.has_perm(perm):
                return function(request, *args, **kwargs)
            else:
                return HttpResponseForbidden()
        return wrapper
    return decorator
