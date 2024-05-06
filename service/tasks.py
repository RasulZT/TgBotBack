import logging

from celery import shared_task
from datetime import datetime
from .models import Reminder
from websocket.consumers import OrderConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from websocket.consumers import ScheduledNotificationConsumer

logger = logging.getLogger(__name__)

@shared_task
def send_reminder():
    # reminders = Reminder.objects.filter(scheduled_time__lte=datetime.now(), is_sent=False)
    # logger.info("Напоминания для отправки: %s", reminders)
    # Отправить уведомление пользователю через канал сообщений
    channel_layer = get_channel_layer()
    ScheduledNotificationConsumer.send_not()
    async_to_sync(channel_layer.group_send)(
        'notification',  # Имя группы WebSocket
        {
            'type': 'send_not',
            'message': "Hi",
        }
    )
    # reminder.is_sent = True
    # reminder.save()



@shared_task
def add(x,y):
    return x+y

