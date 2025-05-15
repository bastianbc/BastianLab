from django.urls import path
from notification.consumers import JobNotificationConsumer
from sequencingfile.routing import LogStreamerConsumer

websocket_urlpatterns = [
    path("ws/notifications/", JobNotificationConsumer.as_asgi()),
    path("ws/logs/", LogStreamerConsumer.as_asgi()),
]
