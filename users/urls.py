from django.urls import path
from .views import TelegramStartView

urlpatterns = [
    path('telegram_start/', TelegramStartView.as_view(), name='telegram_start'),
]