from django.urls import path

from .websocket import consumers

websocket_urlpatterns = [
    path('ws/macbot/', consumers.Consumer.as_asgi()),
]