from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import ChatMessage
from .serializers import ChatMessageSerializer
from .signals import skip_emit


import json

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'

        if self.scope["user"].is_anonymous:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        messages = await self.get_messages()
        await self.send(text_data=json.dumps({
            'type': 'chat.history',
            'messages': messages
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        receiver_id = data['receiver_id']

        sender = self.scope["user"]
        receiver = await self.get_user(receiver_id)

        msg = await self.create_message(sender, receiver, message)

        # Emitimos solo desde aquí
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat.message',
                'message': msg
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat.message',
            'message': event['message']
        }))

    @database_sync_to_async
    def get_user(self, user_id):
        return User.objects.get(id=user_id)

    @database_sync_to_async
    def create_message(self, sender, receiver, message):
        # Señal no debe emitir
        skip_emit()

        chat_message = ChatMessage.objects.create(
            sender=sender,
            receiver=receiver,
            message=message,
            conversation_id=self.conversation_id
        )
        return ChatMessageSerializer(chat_message).data

    @database_sync_to_async
    def get_messages(self):
        user = self.scope['user']
        messages = ChatMessage.objects.filter(
            conversation_id=self.conversation_id
        ).filter(
            Q(sender=user) | Q(receiver=user)
        ).order_by('timestamp')
        return ChatMessageSerializer(messages, many=True).data
