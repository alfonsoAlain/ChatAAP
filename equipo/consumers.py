# equipo/consumers.py

import json
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from .models import Equipo


class EquiposConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "equipos_equipos"

        # Unirse al grupo para recibir eventos de actualización
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Enviar lista inicial de equipos al cliente
        equipos = await self.get_equipos()
        await self.send(text_data=json.dumps({
            'equipos': equipos
        }))

    async def disconnect(self, close_code):
        # Salirse del grupo
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Este consumidor no maneja mensajes entrantes del cliente por ahora
        pass

    async def equipo_actualizado(self, event):
        """Recibe actualizaciones de un equipo desde otros procesos"""
        equipo = event['equipo']
        await self.send(text_data=json.dumps({
            'equipo': equipo
        }))

    @database_sync_to_async
    def get_equipos(self):
        equipos = Equipo.objects.all()
        return [
            {
                'id': equipo.id,
                'nombre': equipo.nombre,
                'cantidad_acciones': equipo.cantidad_acciones,
                'valor_inicial_accion': str(equipo.valor_inicial_accion),
                'limite_diario_variacion_precio': str(equipo.limite_diario_variacion_precio),
                'limite_acciones_jugador': equipo.limite_acciones_jugador,
                'liga_base': equipo.liga_base,
                'id_externo': equipo.id_externo,
            }
            for equipo in equipos
        ]

    @staticmethod
    def enviar_actualizacion_equipo(equipo):
        from django.core.serializers.json import DjangoJSONEncoder

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'equipos_equipos',
            {
                'type': 'equipo_actualizado',
                'equipo': {
                    'id': equipo.id,
                    'nombre': equipo.nombre,
                    'cantidad_acciones': equipo.cantidad_acciones,
                    'valor_inicial_accion': str(equipo.valor_inicial_accion),
                    'liga_base': equipo.liga_base,
                    'id_externo': equipo.id_externo,
                }
            }
        )
