from rest_framework import viewsets, permissions
from rest_framework.authentication import TokenAuthentication

from .models import HistoricoUsuario
from .serializers import HistoricoUsuarioSerializer


class HistoricoUsuarioViewSet(viewsets.ModelViewSet):
    serializer_class = HistoricoUsuarioSerializer
    # authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filtrar el queryset para que solo incluya el histórico del usuario autenticado
        return HistoricoUsuario.objects.filter(usuario=self.request.user)
