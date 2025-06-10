# cartera/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Cartera


@receiver(post_save, sender=Cartera)
def enviar_actualizacion_saldo(sender, instance, **kwargs):
    print(f"***** Signal enviada para usuario {instance.usuario.id}, nuevo saldo: {instance.saldo}")

    # Calcular valor total de acciones del usuario
    from accion.models import Accion  # Ajusta si el import es diferente
    total_valor_acciones = 0

    for accion in Accion.objects.filter(usuario=instance.usuario).select_related('equipo'):
        total_valor_acciones += accion.cantidad * accion.equipo.valor_inicial_accion

    total_valor_acciones = total_valor_acciones + instance.saldo

    # Enviar por WebSocket
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'cartera_{instance.usuario.id}',
        {
            'type': 'send_saldo',
            'saldo': str(instance.saldo),
            'valor_acciones': str(total_valor_acciones),  # 🚨 Esta línea es esencial
        }
    )

# @receiver(post_save, sender=Cartera)
# def enviar_actualizacion_saldo(sender, instance, **kwargs):
#     print(f"**********************************************Signal enviada para usuario {instance.usuario.id}, nuevo saldo: {instance.saldo}")
#
#     channel_layer = get_channel_layer()
#     async_to_sync(channel_layer.group_send)(
#         f'cartera_{instance.usuario.id}',
#         {
#             'type': 'send_saldo',
#             'saldo': str(instance.saldo),
#         }
#     )
