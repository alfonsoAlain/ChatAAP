from rest_framework import serializers
from .models import ChatMessage
from django.contrib.auth.models import User


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = '__all__'
        read_only_fields = ['sender',
        'timestamp']  # usa 'read_only_fields' para campos que no quieres que el usuario edite

class ChatSummarySerializer(serializers.Serializer):
    conversation_id = serializers.CharField()
    contact_name = serializers.CharField()
    profile_image = serializers.CharField(allow_null=True)
    last_message = serializers.CharField()
    last_timestamp = serializers.DateTimeField()
    receiver_id = serializers.IntegerField()