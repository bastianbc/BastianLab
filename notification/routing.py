from django.urls import path, re_path
from notification.consumers import JobNotificationConsumer
from sequencingfile.consumers import LoggingConsumer

websocket_urlpatterns = [
    path("ws/notifications/", JobNotificationConsumer.as_asgi()),
    # path("ws/logs/", LogStreamerConsumer.as_asgi()),
    re_path(r'ws/logging/$', LoggingConsumer.as_asgi()),

]
