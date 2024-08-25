from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from food.models import Order
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from datetime import datetime
@receiver(post_save, sender=Order)
def send_order_info(sender, instance, created, **kwargs):
    if instance.delivery_id:
        telegram_id = instance.delivery_id.telegram_id
    else:
        telegram_id = None  # или другое значение по умолчанию
    if created:
        order_data = {
            'order_id': instance.id,
            'client_id': instance.client_id.telegram_id,
            'delivery_id': telegram_id,
            'status': instance.status,
            'bonus_used': instance.bonus_used,
            'user_name': instance.user_name,
            'address': instance.address,
            'exact_address': instance.exact_address,
            'phone': instance.phone,
            'kaspi_phone': instance.kaspi_phone,
            'client_comment': instance.client_comment,
            'company_id': instance.company_id_id,
            'done_time': instance.done_time.strftime('%H:%M:%S') if instance.done_time else None,
            'bonus_amount': instance.bonus_amount,
            'delivery_price': str(instance.delivery_price),
            'updated_at': instance.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'created_at': instance.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'new_orders',
            {
                'type': 'send_new_order',
                'order': order_data,
            }
        )


@receiver(pre_save, sender=Order)
def save_old_order_state(sender, instance, **kwargs):
    if instance.pk:
        instance._previous_state = Order.objects.get(pk=instance.pk)

@receiver(post_save, sender=Order)
def send_order_update(sender, instance, **kwargs):
    previous_state = getattr(instance, '_previous_state', None)

    if previous_state:
        changes = {}
        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous_state, field_name)
            new_value = getattr(instance, field_name)
            if old_value != new_value:
                # Преобразование datetime объектов в строки формата ISO 8601
                if isinstance(old_value, datetime):
                    old_value = old_value.isoformat()
                if isinstance(new_value, datetime):
                    new_value = new_value.isoformat()

                changes[field_name] = new_value

        if changes:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'orders',
                {
                    'type': 'order_update',
                    'order_id': instance.id,
                    'changes': changes
                }
            )