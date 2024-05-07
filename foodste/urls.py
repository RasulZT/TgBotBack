"""
URL configuration for foodste project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include

import my_auth.urls
import food.urls,loyalty.urls,service.urls
from django.conf.urls.static import static
from django.conf import settings
from .views import get_image
import websocket.urls

from .yasg import urlpatterns as doc_urls

urlpatterns = [
    path('azim/', admin.site.urls),
    path('auth/', include(my_auth.urls)),
    path('food/', include('food.urls')),
    path('loy/', include('loyalty.urls')),
    path('service/', include('service.urls')),
    path('media/images/<str:image_name>/', get_image, name='get_image'),
    path("ws/", include("websocket.urls")),
]

urlpatterns += doc_urls
