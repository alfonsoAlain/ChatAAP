import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from exceptiongroup import catch

from .models import Cartera

class CarteraConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if user.is_authenticated:
            self.user = user
            self.group_name = f'cartera_{user.id}'
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()

            saldo = await self.get_saldo()
            acciones = await self.get_total_acciones() + saldo
            await self.send(json.dumps({'saldo': str(saldo),'valor_acciones': str(acciones)}))
        else:
            await self.close(code=4401)

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        # No manejamos mensajes del cliente en este caso
        pass

    async def send_saldo(self, event):
        saldo = event.get('saldo')
        valor_acciones = event.get('valor_acciones', None)

        data = {'saldo': str(saldo)}
        if valor_acciones is not None:
            data['valor_acciones'] = str(valor_acciones)

        await self.send(json.dumps(data))
        # saldo = event['saldo']
        # await self.send(json.dumps({'saldo': str(saldo)}))

    @database_sync_to_async
    def get_saldo(self):
        try:
            cartera = Cartera.objects.get(usuario=self.user)
            return cartera.saldo
        except Cartera.DoesNotExist:
            return 0

    @database_sync_to_async
    def get_total_acciones(self):
        try: # Calcular valor total de acciones del usuario
            from accion.models import Accion  # Ajusta si el import es diferente
            total_valor_acciones = 0

            for accion in Accion.objects.filter(usuario=self.user).select_related('equipo'):
                total_valor_acciones += accion.cantidad * accion.equipo.valor_inicial_accion
            return total_valor_acciones
        except Accion.DoesNotExist:
            return 0


