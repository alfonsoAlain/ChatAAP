from rest_framework import viewsets

from .serializers import PartidoVotacionUsuarioSerializer
from .models import PartidoVotacionUsuario


class PartidoVotacionUsuarioViewSet(viewsets.ModelViewSet):
    queryset = PartidoVotacionUsuario.objects.all()
    serializer_class = PartidoVotacionUsuarioSerializer
