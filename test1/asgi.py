"""
ASGI config for test1 project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/asgi/
"""
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from notification.routing import websocket_urlpatterns as notification_patterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test1.settings')

application = ProtocolTypeRouter({
    # HTTP requests are handled by Django’s ASGI application
    "http": get_asgi_application(),

    # WebSocket connections go through the Auth middleware
    # into your URLRouter (notification.routing.websocket_urlpatterns)
    "websocket": AuthMiddlewareStack(
        URLRouter(notification_patterns)
    ),
})
