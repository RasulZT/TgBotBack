from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import CustomUser  # Импортируем модель CustomUser из вашего приложения

# Регистрируем модель CustomUser в админской панели
admin.site.register(CustomUser)
