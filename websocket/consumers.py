import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from food.models import Order
from django.core.serializers.json import DjangoJSONEncoder

class OrderConsumer(WebsocketConsumer):
    def connect(self):
        self.group_name = 'orders'
        async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)
        self.accept()

        # Отправляем все существующие заказы при подключении клиента
        orders = Order.objects.all()
        for order in orders:
            self.send_order_info(order)

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(self.group_name, self.channel_name)

    def send_order_info(self, order):
        # Отправляем информацию о заказе клиенту через WebSocket
        self.send(text_data=json.dumps({
            'type': 'order_info',
            'order_id': order.id,
            'status': order.status,
            # Добавьте другие поля здесь при необходимости
        }))

    def order_update(self, event):
        order_id = event['order_id']
        status = event['status']
        # Обновляем данные заказа на вашей HTML-странице
        self.send(text_data=json.dumps({
            'type': 'order_update',
            'order_id': order_id,
            'status': status,
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