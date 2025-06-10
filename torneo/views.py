from rest_framework import viewsets, status
from rest_framework.response import Response

from usuario.models import Usuario
from .models import Torneo  
from .serializers import TorneoSerializer

class TorneoViewSet(viewsets.ModelViewSet):  
    queryset = Torneo.objects.all()  
    serializer_class = TorneoSerializer

    def update(self, request, *args, **kwargs):
        torneo = self.get_object()
        jugadores_data = request.data.get('jugadores', [])

        # Agregar cada jugador a la lista de jugadores
        for jugador_id in jugadores_data:
            try:
                jugador = Usuario.objects.get(id=jugador_id)
                torneo.jugadores.add(jugador)
            except Usuario.DoesNotExist:
                return Response(
                    {"error": f"Usuario con id {jugador_id} no existe."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Llamar al método de actualización original para manejar otros campos
        return super().update(request, *args, **kwargs)
