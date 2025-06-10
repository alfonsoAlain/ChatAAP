from django.http import HttpResponse
from pyexpat.errors import messages
from requests import Response
from rest_framework import viewsets, permissions, status
from .models import TransaccionPendiente
from .serializers import TransaccionPendienteSerializer
from django.shortcuts import get_object_or_404
from equipo.models import Equipo


class TransaccionPendienteViewSet(viewsets.ModelViewSet):
    queryset = TransaccionPendiente.objects.all()
    serializer_class = TransaccionPendienteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        equipo_id = self.request.data.get('equipo_id')

        # Obtengo la instancia del Equipo
        equipo = get_object_or_404(Equipo, id=equipo_id)

        # Guarda la transacción, pasando la instancia del equipo y el usuario
        serializer.save(equipo=equipo, usuario=self.request.user)
        # def perform_create(self, serializer):
    #     serializer.save()
    #     # serializer.save(usuario=self.request.user)Asi estaba y funcionaba

    def get_queryset(self):
        # Excluye las transacciones del usuario autenticado
        user = self.request.user
        queryset = TransaccionPendiente.objects.exclude(usuario=user)
        return queryset

    # def destroy(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     self.perform_destroy(instance)
    #     return Response(status=status.HTTP_204_NO_CONTENT)

class MisTransaccionPendienteViewSet(viewsets.ModelViewSet):
    queryset = TransaccionPendiente.objects.all()
    serializer_class = TransaccionPendienteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        equipo_id = self.request.data.get('equipo_id')

        # Obtengo la instancia del Equipo
        equipo = get_object_or_404(Equipo, id=equipo_id)

        # Guarda la transacción, pasando la instancia del equipo y el usuario
        serializer.save(equipo=equipo, usuario=self.request.user)

    def get_queryset(self):
        # Excluye las transacciones del usuario autenticado
        user = self.request.user
        queryset = TransaccionPendiente.objects.filter(usuario=user)
        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        # Usamos el perform_destroy del serializer
        serializer.perform_destroy(instance)

        return HttpResponse(
            "Transacción eliminada correctamente.",
            status=status.HTTP_204_NO_CONTENT,
            content_type="application/json"
        )
        # return HttpResponse(
        #     status = status.HTTP_204_NO_CONTENT,
        # )


