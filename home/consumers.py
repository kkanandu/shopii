# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from home.models import ChatMessage
from channels.db import database_sync_to_async

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.sender = self.scope['user']
        self.receiver_id = self.scope['url_route']['kwargs']['receiver_id']
        self.room_group_name = self.get_room_name(self.sender.id, self.receiver_id)

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    def get_room_name(self, user1_id, user2_id):
        """Consistent room name for user pair"""
        sorted_ids = sorted([int(user1_id), int(user2_id)])
        return f'chat_{sorted_ids[0]}_{sorted_ids[1]}'

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        sender = self.scope['user']

        # Save to database
        receiver = await self.get_receiver(self.receiver_id)
        await self.save_message(sender, receiver, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender.username
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender']
        }))

    @database_sync_to_async
    def get_receiver(self, receiver_id):
        from django.contrib.auth import get_user_model
        return get_user_model().objects.get(id=receiver_id)

    @database_sync_to_async
    def save_message(self, sender, receiver, content):
        from .models import ChatMessage
        ChatMessage.objects.create(sender=sender, receiver=receiver, content=content)
