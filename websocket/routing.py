from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from .consumers import OrderConsumer, NewOrderConsumer,ScheduledNotificationConsumer

websocket_urlpatterns = [
    path('ws/orders/', OrderConsumer.as_asgi()),
    path('ws/new_orders/', NewOrderConsumer.as_asgi()),
    path('ws/send_not/',ScheduledNotificationConsumer.as_asgi())# Добавлен новый путь
]

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
