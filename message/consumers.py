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

        content = data['content_encrypted']
        aes_sender = data['aes_key_for_sender']
        aes_receiver = data['aes_key_for_receiver']
        receiver_id = data['receiver_id']

        sender = self.scope["user"]
        receiver = await self.get_user(receiver_id)

        msg = await self.create_message(sender, receiver, content, aes_sender, aes_receiver)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat.message',
                'message': {
                    'id': msg.id,
                    'conversation_id': msg.conversation_id,
                    'sender': msg.sender.id,
                    'receiver': msg.receiver.id,
                    'message': msg.content_encrypted,
                    'timestamp': msg.timestamp.isoformat(),
                    'is_read': msg.is_read,
                    'aes_key_for_receiver': msg.aes_key_for_receiver,
                    'aes_key_for_sender': msg.aes_key_for_sender,
                }
            }
        )

    async def chat_message(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'type': 'chat.message',
            'message': {
                'id': message['id'],
                'conversation_id': message['conversation_id'],
                'sender': message['sender'],
                'receiver': message['receiver'],
                'message': message['message'],
                'timestamp': message['timestamp'],
                'is_read': message['is_read'],
                'aes_key_for_receiver': message['aes_key_for_receiver'],
                'aes_key_for_sender': message['aes_key_for_sender'],
            }
        }))

    @database_sync_to_async
    def get_user(self, user_id):
        return User.objects.get(id=user_id)

    @database_sync_to_async
    def create_message(self, sender, receiver, content, aes_sender, aes_receiver):
        skip_emit()
        chat_message = ChatMessage.objects.create(
            sender=sender,
            receiver=receiver,
            content_encrypted=content,
            aes_key_for_sender=aes_sender,
            aes_key_for_receiver=aes_receiver,
            conversation_id=self.conversation_id
        )
        return chat_message
        # return ChatMessageSerializer(chat_message, context={'user': sender}).data

    @database_sync_to_async
    def get_messages(self):
        user = self.scope['user']
        messages = ChatMessage.objects.filter(
            conversation_id=self.conversation_id
        ).filter(
            Q(sender=user) | Q(receiver=user)
        ).order_by('timestamp')
        return ChatMessageSerializer(messages, many=True).data
