from django.db import models
from usuario.models import Usuario

class ChatMessage(models.Model):
    sender = models.ForeignKey(Usuario, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(Usuario, related_name='received_messages', on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    conversation_id = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "Chat Message"
        verbose_name_plural = "Chat Messages"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.sender.username} to {self.receiver.username} at {self.timestamp}"