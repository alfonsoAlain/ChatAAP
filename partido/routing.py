from django.urls import path
from .consumers import PartidoConsumer

websocket_urlpatterns = [
    path('ws/partidos/', PartidoConsumer.as_asgi()),  # Este es el endpoint para WebSocket
]