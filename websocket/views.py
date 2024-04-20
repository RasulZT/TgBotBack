from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from food.models import Order
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Order)
def send_order_info(sender, instance, created, **kwargs):
    print("AHAHAHA")
    print(instance.client_id.telegram_id)
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



@receiver(post_save, sender=Order)
def send_order_update(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'orders',
        {
            'type': 'order_update',
            'order_id': instance.id,
            'status': instance.status,
            # Add other fields here if needed
        }
    )


# def update_order_status(request, order_id):
#     # Получаем заказ по его идентификатору
#     order = get_object_or_404(Order, pk=order_id)
#
#     # Меняем статус заказа
#     new_status = request.POST.get('new_status')
#     order.status = new_status
#     order.save()
#
#     # Отправляем сообщение о обновлении статуса заказа через WebSocket
#     channel_layer = get_channel_layer()
#     async_to_sync(channel_layer.group_send)(
#         'orders',  # Название группы (канала)
#         {
#             'type': 'order_update',  # Тип сообщения, который обрабатывается consumer'ом
#             'order_id': order.id,
#             'status': new_status,
#         }
#     )
#
#     return JsonResponse({'status': 'success'})

