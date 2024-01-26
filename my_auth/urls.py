from django.urls import path

from .views import RegisterView, UserView,CustomTokenView
from rest_framework.authtoken import views

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('login', views.obtain_auth_token, name='login'),
    path('user', UserView.as_view(), name='getUser'),
    path('create_token', CustomTokenView.as_view(), name='getUser'),
]
