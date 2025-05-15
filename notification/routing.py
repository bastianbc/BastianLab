from django.urls import path
from notification.consumers import JobNotificationConsumer
from sequencingfile.consumers import LogStreamerConsumer

websocket_urlpatterns = [
    path("ws/notifications/", JobNotificationConsumer.as_asgi()),
    # path("ws/logs/", LogStreamerConsumer.as_asgi()),
]
