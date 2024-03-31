# chat/urls.py
from django.urls import path

from . import views,consumers


urlpatterns = [
    path('orders/', consumers.OrderConsumer.as_asgi()),
    path('new_orders/', consumers.NewOrderConsumer.as_asgi()),


]