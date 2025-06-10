import base64

from channels.db import database_sync_to_async
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime

from django.core.paginator import Paginator

from .models import Partido


def default_json_encoder(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    else:
        return obj.__dict__


class PartidoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # self.group_name = 'partidos_group'
        self.estado = None
        # await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        estado = data.get('estado')

        # Cambiar el group_name basado en el estado que se recibió
        self.group_name = f'partidos_group_{estado}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        dia_partido = data.get('diaPartido')
        torneo_id = data.get('torneo')
        self.estado = data.get('estado')
        page = data.get('page', 1)  # Por defecto, página 1
        per_page = data.get('perPage', 10)  # Por defecto 10 por página
        print(self.estado)
        partidos = await self.get_queryset(dia_partido, torneo_id, self.estado, page, per_page)
        await self.sendUpdatedPartidos(partidos)

    async def sendUpdatedPartidos(self, partidos):
        print(f"Modificando: {self.group_name}")
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'send_partidos_update',
                'partidos': partidos,
            }
        )

    async def send_partidos_update(self, event):
        partidos = event['partidos']
        await self.send(text_data=json.dumps(partidos, default=default_json_encoder))

    @database_sync_to_async
    def get_queryset(self, dia_partido, torneo_id, estado, page=1, per_page=10):
        queryset = Partido.objects.all()
        filtros = {}

        if dia_partido:
            filtros['diaPartido'] = dia_partido
        if torneo_id:
            filtros['torneo_id'] = torneo_id
        if estado:
            filtros['estado'] = estado

        if filtros:
            queryset = queryset.filter(**filtros)

        queryset = queryset.order_by('fecha')

            # Paginación
        paginator = Paginator(queryset, per_page)  # Por defecto, por página: `per_page`
        partidos = paginator.get_page(page)  # Obtiene la página solicitada

        resultados = []
        for partido in partidos:
            equipo_local_nombre = partido.equipo_local.nombre
            equipo_local = partido.equipo_local.id
            equipo_visitante_nombre = partido.equipo_visitante.nombre
            equipo_visitante = partido.equipo_visitante.id

            # Convertir escudos a base64
            equipo_local_escudo = self.convert_image_to_base64(partido.equipo_local.escudo)
            equipo_visitante_escudo = self.convert_image_to_base64(partido.equipo_visitante.escudo)

            resultados.append({
                'id': partido.id,
                'equipo_local_nombre': equipo_local_nombre,
                'equipo_local': equipo_local,
                'equipo_visitante_nombre': equipo_visitante_nombre,
                'equipo_visitante': equipo_visitante,
                'equipo_local_escudo': equipo_local_escudo,
                'equipo_visitante_escudo': equipo_visitante_escudo,
                'equipo_local_goles': partido.equipo_local_goles,
                'equipo_visitante_goles': partido.equipo_visitante_goles,
                'fecha': partido.fecha,
                'torneo_id': partido.torneo_id,
                'estado': partido.estado,
                'diaPartido': partido.diaPartido,
                'id_externo': partido.id_externo,
                'estado_anterior': partido.estado_anterior,
                'resultado': f'{partido.equipo_local_goles}-{partido.equipo_visitante_goles}'
            })

        return resultados

    def convert_image_to_base64(self, image_field):
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