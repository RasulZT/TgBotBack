# файл celery.py

from celery import Celery
from django.conf import settings
import os

# Указываем Django settings модуль для Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodste.settings')

app = Celery('foodste')

# Загружаем настройки из Django settings
app.config_from_object('django.conf:settings',namespace='CELERY')

# Автоматически обнаруживаем задачи в приложениях Django
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
