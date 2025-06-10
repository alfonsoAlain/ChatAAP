from rest_framework.response import Response
from rest_framework import viewsets, permissions

# from accion.serializers import AccionSerializer
# from transaccion_pendiente.models import TransaccionPendiente
# # from . import serializers
from .models import Accion
from .serializers import AccionSerializer

class AccionViewSet(viewsets.ModelViewSet):
    queryset = Accion.objects.all()
    serializer_class = AccionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Devuelve solo las acciones del usuario autenticado
        return Accion.objects.filter(usuario=self.request.user)
    def perform_create(self, serializer):
        # Pasar el usuario autenticado al serializer
        serializer.save(usuario_autenticado=self.request.user)

#con http por probar
# class AccionViewSet(viewsets.ModelViewSet):
#     queryset = Accion.objects.all()
#     serializer_class = AccionSerializer
#     permission_classes = [permissions.IsAuthenticated]
#
#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)  # Lanza ValidationError si no es válido
#         self.perform_create(serializer)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#
#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)  # Esto lanzará ValidationError automáticamente
#         self.perform_create(serializer)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#
#     def get_queryset(self):
#         # Retorna solo las acciones del usuario autenticado
#         user = self.request.user
#         return Accion.objects.filter(usuario=user)

