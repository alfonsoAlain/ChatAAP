import base64

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Partido


@receiver(post_save, sender=Partido)
def partido_changed(sender, instance, created, **kwargs):
    print("Signal ejecutada: partido guardado")
    channel_layer = get_channel_layer()

    equipo_local_escudo = convert_image_to_base64(instance.equipo_local.escudo)
    equipo_visitante_escudo = convert_image_to_base64(instance.equipo_visitante.escudo)

    partido_data = {
        'id': instance.id,
        'diaPartido': instance.diaPartido,
        'torneo_id': instance.torneo_id,
        'estado': instance.estado,

        'equipo_local_nombre': instance.equipo_local.nombre,
        'equipo_local': instance.equipo_local.id,
        'equipo_visitante_nombre': instance.equipo_visitante.nombre,
        'equipo_visitante': instance.equipo_visitante.id,
        'equipo_local_escudo': equipo_local_escudo,
        'equipo_visitante_escudo': equipo_visitante_escudo,
        'equipo_local_goles': instance.equipo_local_goles,
        'equipo_visitante_goles': instance.equipo_visitante_goles,
        'fecha': instance.fecha,
        'torneo_id': instance.torneo.id,
        'estado': instance.estado,
        'diaPartido': instance.diaPartido,
        'id_externo': instance.id_externo,
        'estado_anterior': instance.estado_anterior,
        'resultado': f'{instance.equipo_local_goles}-{instance.equipo_visitante_goles}'
    }

    # Crea el nombre del grupo basado en el estado del partido
    group_name = f'partidos_group_{instance.estado}'

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'send_partidos_update',
            'partidos': [partido_data],  # puedes enviar los partidos restantes si lo prefieres
        }
    )


@receiver(post_delete, sender=Partido)
def partido_deleted(sender, instance, **kwargs):
    print("Partido eliminado:", instance)  # Agregar esta línea
    channel_layer = get_channel_layer()

    # Crea el nombre del grupo basado en el estado del partido
    group_name = f'partidos_group_{instance.estado}'

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'send_partidos_update',
            'partidos': []  # O envía la lista de partidos restantes según tu lógica
        }
    )


def convert_image_to_base64(image_field):
    if image_field and hasattr(image_field, 'path'):
        try:
            with open(image_field.path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                return encoded_string
        except FileNotFoundError:
            # Manejar la ausencia del archivo
            print(f"Archivo no encontrado: {image_field.path}")
            return None  # o devolver una imagen por defecto
    return None  # O devuelve una cadena vacía o un valor por defecto
