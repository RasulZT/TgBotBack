import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from food.models import Order
from django.core.serializers.json import DjangoJSONEncoder
from channels.layers import get_channel_layer
class OrderConsumer(WebsocketConsumer):
    def connect(self):
        self.group_name = 'orders'
        async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)
        self.accept()
        print(get_channel_layer().group_send)
        # Отправляем все существующие заказы при подключении клиента
        orders = Order.objects.all()
        for order in orders:
            self.send_order_info(order)

    def receive(self, text_data):
        pass  # не требуется обработка сообщений от клиента

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(self.group_name, self.channel_name)

    def send_order_info(self, order):
        # Отправляем информацию о заказе клиенту через WebSocket
        if order.delivery_id:
            tg_id=order.delivery_id.telegram_id
        else:
            tg_id=0
        self.send(text_data=json.dumps({
            'type': 'order_info',
            'order_id': order.id,
            'status': order.status,
            'delivery_id':tg_id,
            # Добавьте другие поля здесь при необходимости
        }))

    def order_update(self, event):
        print(event)
        order_id = event['order_id']
        status = event['status']
        order=Order.objects.get(id=order_id)
        if order.delivery_id:
            delivery_id=order.delivery_id.telegram_id
        else:
            delivery_id = 0
        rejected_text=order.rejected_text
        # Обновляем данные заказа на вашей HTML-странице
        self.send(text_data=json.dumps({
            'type': 'order_update',
            'order_id': order_id,
            'status': status,
            'delivery_id': delivery_id,
            'rejected_text':rejected_text

            # Добавьте другие поля здесь при необходимости
        }))

class NewOrderConsumer(WebsocketConsumer):
    def connect(self):
        self.group_name = 'new_orders'
        async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(self.group_name, self.channel_name)

    def receive(self, text_data):
        pass  # не требуется обработка сообщений от клиента

    def send_new_order(self, event):
        order_data = event['order']
        self.send(text_data=json.dumps({
            'type': 'new_order',
            'order_data': order_data,
        }, cls=DjangoJSONEncoder))  # Используем DjangoJSONEncoder для сериализации объектов Django


class ScheduledNotificationConsumer(WebsocketConsumer):
    def connect(self):
        self.group_name = 'notification'
        async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)
        print("NOTIF")
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(self.group_name, self.channel_name)

    def send_not(self, event):
        message = event['message']
        user_id=event['user_id']
        # logger.info(f"WebSocket received message: {message}")
        self.send(text_data=json.dumps({
            'type': 'send_not',
            'user_id':user_id,
            'message': message
        },ensure_ascii=False))

