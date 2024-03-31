from django.test import TestCase
from channels.testing import WebsocketCommunicator
from websocket.consumers import OrderConsumer
import json

class WebSocketTests(TestCase):
    async def test_order_update(self):
        communicator = WebsocketCommunicator(OrderConsumer, "/ws/orders/")
        connected, _ = await communicator.connect()

        message = {
            "type": "status_update",
            "order_id": 123,
            "status": "done"
        }
        await communicator.send_json_to(message)

        response = await communicator.receive_json_from()
        self.assertEqual(response, {
            "type": "order_update",
            "order_id": 123,
            "status": "done"
        })

        await communicator.disconnect()
