import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from food.models import Order
from datetime import datetime

from django.core.serializers.json import DjangoJSONEncoder
from channels.layers import get_channel_layer


class OrderConsumer(WebsocketConsumer):
    def connect(self):
        self.group_name = 'orders'
        async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(self.group_name, self.channel_name)

    def order_update(self, event):
        order_id = event['order_id']
        changes = event['changes']
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Order with id {order_id} does not exist.'
            }))
            return

        # Отправляем только измененные данные
        self.send(text_data=json.dumps({
            'type': 'order_update',
            'order_id': order_id,
            'changes': changes
        },ensure_ascii=False))
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

