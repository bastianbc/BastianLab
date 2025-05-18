from django.urls import path, re_path
from notification.consumers import JobNotificationConsumer
from sequencingfile.consumers import LoggingConsumer
from sequencingfile.walk_labshare import FileTreeConsumer

websocket_urlpatterns = [
    path("ws/notifications/", JobNotificationConsumer.as_asgi()),
    re_path(r"ws/file-tree/$", FileTreeConsumer.as_asgi()),

]
