import logging

from celery import shared_task
from datetime import datetime
from .models import Reminder
from websocket.consumers import OrderConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from websocket.consumers import ScheduledNotificationConsumer
from django.utils import timezone
from pytz import timezone as tz

# @shared_task
# def send_reminder_notification():
#     message = reminder.message
#     channel_layer = get_channel_layer()
#     async_to_sync(channel_layer.group_send)(
#         'notification',
#         {
#             'type': 'send_not',
#             'message': message
#             # Добавьте другие поля здесь при необходимости
#         }
#     )
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)
@shared_task
def send_periodic_notification():
    message = "Periodic reminder message"
    channel_layer = get_channel_layer()
    logger.info(channel_layer)
    async_to_sync(channel_layer.group_send)(
        'notification',
        {
            'type': 'send_not',
            'message': message
        }
    )
    logger.info("Message sent to channel layer")


@shared_task
def send_scheduled_notifications():
    # Получаем текущее время в часовом поясе Алматы
    almaty_timezone = tz('Asia/Almaty')
    now_almaty = timezone.now().astimezone(almaty_timezone)
    logger.info(now_almaty)
    # Получаем все напоминания, у которых scheduled_time меньше или равно текущему времени
    reminders = Reminder.objects.filter(scheduled_time__lte=now_almaty, is_sent=False)
    logger.info(reminders)
    for reminder in reminders:
        message= reminder.message
        user_id= reminder.user.telegram_id
        logger.info(reminder)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'notification',
            {
                'type': 'send_not',
                'user_id':user_id,
                'message': message
            }
        )
        reminder.is_sent = True
        reminder.save()


@shared_task
def add(x,y):
    return x+y

