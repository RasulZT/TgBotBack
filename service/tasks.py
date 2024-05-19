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
        message = reminder.message
        user_id = reminder.user_id
        logger.info(reminder)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'notification',
            {
                'type': 'send_not',
                'user_id': user_id,
                'message': message
            }
        )
        reminder.is_sent = True
        reminder.save()


from django.db import transaction
from .models import ArchivedOrder
from food.models import Order
from django.db import connection

def reset_order_id_sequence():
    with connection.cursor() as cursor:
        cursor.execute("ALTER SEQUENCE food_order_id_seq RESTART WITH 1;")

def archive_orders():
    orders_to_archive = Order.objects.all()

    with transaction.atomic():
        for order in orders_to_archive:
            archived_order = ArchivedOrder(
                original_order_id=order.id,
                client_id=order.client_id,
                delivery_id=order.delivery_id,
                status=order.status,
                bonus_used=order.bonus_used,
                is_delivery=order.is_delivery,
                user_name=order.user_name,
                address=order.address,
                exact_address=order.exact_address,
                phone=order.phone,
                kaspi_phone=order.kaspi_phone,
                rating=order.rating,
                rejected_text=order.rejected_text,
                client_comment=order.client_comment,
                company_id=order.company_id,
                done_time=order.done_time,
                bonus_amount=order.bonus_amount,
                delivery_price=order.delivery_price,
                updated_at=order.updated_at,
                created_at=order.created_at
            )
            archived_order.save()
            archived_order.actions.set(order.actions.all())
            archived_order.products.set(order.products.all())

        Order.objects.all().delete()

@shared_task
def restart_index():
    archive_orders()
    reset_order_id_sequence()
