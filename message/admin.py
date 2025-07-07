from django.contrib import admin

from message.models import ChatMessage


# Register your models here.
@admin.register(ChatMessage)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'message', 'timestamp', 'is_read')
