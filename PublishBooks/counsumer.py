from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.layers import get_channel_layer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.group_name = f"notifications_{self.user_id}"
        self.channel_layer = get_channel_layer()

        if self.channel_layer:
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
        await self.accept()
        print(f"User {self.user_id} connected to WebSocket.")

    async def disconnect(self, close_code):
        if self.channel_layer:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        print(f"Received from {self.user_id}: {data}")
        await self.send(text_data=json.dumps({
            'response': f"Received: {data}"
        }))

    async def send_notification(self, event):
        message = event.get('message', 'No message provided')
        print("Sending notification:", message)
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'message': message
        }))
