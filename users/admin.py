from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Client

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['id', 'telegram_fullname', 'role', 'created_at', 'updated_at']
    search_fields = ['id', 'telegram_fullname']  # Добавьте поля для поиска
    list_filter = ['role']  # Добавьте поля для фильтрации
