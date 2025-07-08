from django.db.utils import OperationalError
from django.http import HttpResponse


class DatabaseCredentialMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except OperationalError as e:
            if 'authentication failed' in str(e).lower():
                # Optionally trigger refresh or alert
                return HttpResponse("Database authentication error. Please try again shortly.", status=503)
            raise
