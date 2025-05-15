# sequencingfile/routing.py
from django.urls import re_path
from .consumers import LogStreamerConsumer

# websocket_urlpatterns = [
#     re_path(r'^ws/logs/?$', LogStreamerConsumer.as_asgi()),
# ]
