from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/chat/', consumers.ChatConsumer.as_asgi()),  # Consommateur pour le chat général
    path('ws/private_chat/<str:username>/', consumers.PrivateChatConsumer.as_asgi()),  # Consommateur pour le chat privé
]
