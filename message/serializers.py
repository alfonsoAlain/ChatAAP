from rest_framework import serializers
from .models import ChatMessage
from django.contrib.auth import get_user_model



class ChatMessageSerializer(serializers.ModelSerializer):
    aes_key = serializers.SerializerMethodField()
    message = serializers.CharField(source='content_encrypted')

    sender_id = serializers.IntegerField(source='sender.id', read_only=True)
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    sender_profile_image_url = serializers.CharField(source='sender.profile_image_url', read_only=True)  # ajustar según tu modelo
    sender_public_key = serializers.CharField(source='sender.public_key', read_only=True)  # ajustar según tu modelo

    class Meta:
        model = ChatMessage
        fields = [
            'id', 'conversation_id', 'sender', 'receiver', 'sender_id', 'sender_name', 'sender_profile_image_url',
            'sender_public_key', 'timestamp', 'is_read', 'message', 'aes_key', 'aes_key_for_sender', 'aes_key_for_receiver'
        ]

    def get_aes_key(self, obj):
        user = self.context.get('user')
        if user == obj.sender:
            return obj.aes_key_for_sender
        elif user == obj.receiver:
            return obj.aes_key_for_receiver
        else:
            return None

class ChatMessageDetailedSerializer(ChatMessageSerializer):
    contact_name = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()
    public_key = serializers.SerializerMethodField()
    receiver_id = serializers.SerializerMethodField()

    class Meta(ChatMessageSerializer.Meta):
        fields = ChatMessageSerializer.Meta.fields + [
            'contact_name', 'profile_image', 'public_key', 'receiver_id'
        ]

    def get_contact_name(self, obj):
        user = self.context.get('user')
        contact = obj.receiver if obj.sender == user else obj.sender
        return contact.username

    def get_profile_image(self, obj):
        request = self.context.get('request')
        user = self.context.get('user')
        contact = obj.receiver if obj.sender == user else obj.sender
        if getattr(contact, 'profile_image', None):
            return request.build_absolute_uri(contact.profile_image.url)
        return None

    def get_public_key(self, obj):
        user = self.context.get('user')
        contact = obj.receiver if obj.sender == user else obj.sender
        return contact.public_key

    def get_receiver_id(self, obj):
        user = self.context.get('user')
        contact = obj.receiver if obj.sender == user else obj.sender
        return contact.id


User = get_user_model()

class ChatSummarySerializer(serializers.Serializer):
    conversation_id = serializers.CharField()
    contact_name = serializers.CharField()
    profile_image = serializers.CharField(allow_null=True)
    last_message = serializers.CharField()
    last_timestamp = serializers.DateTimeField()
    receiver_id = serializers.IntegerField()

class ConversationStartSerializer(serializers.Serializer):
    conversation_id = serializers.CharField()
    contact_name = serializers.CharField()
    profile_image = serializers.CharField(allow_null=True)
    last_message = serializers.CharField(allow_blank=True)
    last_timestamp = serializers.DateTimeField()
    receiver_id = serializers.IntegerField()
    public_key = serializers.CharField(allow_blank=True, allow_null=True)