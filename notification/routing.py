from django.urls import path
from notification.consumers import JobNotificationConsumer

websocket_urlpatterns = [
    # path("ws/notifications/", JobNotificationConsumer.as_asgi()),
]
