import threading
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ChatMessage
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

# Flag por hilo para detectar origen
thread_local = threading.local()

def skip_emit():
    thread_local.skip_emit = True

def should_skip_emit():
    return getattr(thread_local, 'skip_emit', False)

@receiver(post_save, sender=ChatMessage)
def send_chat_message_to_websocket(sender, instance, created, **kwargs):
    print("19",instance)
    print("Campos de instance:", instance.__dict__)
    if not created:
        return
    if should_skip_emit():
        # Solo una vez
        thread_local.skip_emit = False
        return

    emit_message_to_ws(instance)

def emit_message_to_ws(instance):
    channel_layer = get_channel_layer()
    print("Clave AES receptor:", instance.aes_key_for_receiver)
    async_to_sync(channel_layer.group_send)(
        f"chat_{instance.conversation_id}",
        {
            "type": "chat.message",
            "message": {
                "id": instance.id,
                "conversation_id": instance.conversation_id,
                "sender": instance.sender.id,
                "receiver": instance.receiver.id,
                "message": instance.content_encrypted,
                "timestamp": instance.timestamp.isoformat(),
                "is_read": instance.is_read,
                "aes_key_for_receiver": instance.aes_key_for_receiver,
                "aes_key_for_sender": instance.aes_key_for_sender,
            }
        }
    )
