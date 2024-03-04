from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import *
from rest_framework.authtoken import views

urlpatterns = [
    path('register/', UserRegistrationAPIView.as_view(), name='user_registration'),
    path('user/<int:telegram_id>/', UserByTelegramIdAPIView.as_view(), name='user-detail'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/update/', UpdateTokenView.as_view(), name='update_token')
]
