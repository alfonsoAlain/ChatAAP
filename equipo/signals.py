from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Equipo
from .consumers import EquiposConsumer


@receiver(post_save, sender=Equipo)
def equipo_actualizado_signal(sender, instance, **kwargs):
    """
    Se llama automáticamente cuando se guarda un equipo.
    Llama al método del consumidor que notifica por WebSocket.
    """
    EquiposConsumer.enviar_actualizacion_equipo(instance)