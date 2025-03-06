import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Notification

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Accept the WebSocket connection
        self.user = self.scope["user"]
        self.room_group_name = f"notification_{self.user.id}"

        # Join the group based on user ID
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        await self.send(text_data=json.dumps({
            'message': "Connected to WebSocket"
        }))

    async def disconnect(self, close_code):
        # Leave the group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Receive messages from WebSocket
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to WebSocket group
        # Broadcast to the group that the user is part of
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send_notification',  # This refers to the method below
                'message': message
            }
        )

    # This method is triggered by group_send and sends the message to the WebSocket client
    async def send_notification(self, event):
        message = event['message']
        print("Sending Notification to WebSocket")
        print(message)

        # Send notification to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
             "id": event["id"]
        }))
