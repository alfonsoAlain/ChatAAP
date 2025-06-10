from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action

from notificacion.models import Notificacion, NotificacionUsuario
from notificacion.serializers import NotificacionSerializer, NotificacionUsuarioSerializer
from django.utils import timezone



class NotificacionViewSet(viewsets.ModelViewSet):
    queryset = Notificacion.objects.all()
    serializer_class = NotificacionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Obtiene el usuario autenticado
        user = self.request.user
        # Filtra las notificaciones del usuario autenticado
        return Notificacion.objects.filter(usuarios=user)


class Notification:
    pass


class NotificationUsuarioViewSet(viewsets.ModelViewSet):
    queryset = NotificacionUsuario.objects.all()
    serializer_class = NotificacionUsuarioSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filtra las lecturas de notificaciones para el usuario autenticado
        usuario = self.request.user
        print("usuario get_queryset", usuario)
        return NotificacionUsuario.objects.filter(usuario=usuario)

    @action(detail=False, methods=['post'])
    def marcar_como_leida(self, request, pk=None):
        notificacion_id = request.data.get('notificacion')
        notificacion = get_object_or_404(Notificacion, id=notificacion_id)

        # Crea o actualiza la lectura de la notificación
        notification_read, created = NotificacionUsuario.objects.update_or_create(
            usuario=request.user,
            notificacion=notificacion,
            defaults={'fecha_leido': timezone.now()}
        )

        return Response({'status': 'notificación marcada como leída'}, status=status.HTTP_200_OK)

    # @action(detail=True, methods=['delete'])
    # def eliminar_notificacion(self, request, pk=None):
    #     notificacion_usuario = get_object_or_404(NotificacionUsuario, id=pk, usuario=request.user)
    #     notificacion_usuario.delete()
    #     return Response({'status': 'notificación eliminada'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def get_by_notification_id(self, request):
        notificacion_id = request.query_params.get('notificacion_id')
        print("notificacion_id", notificacion_id)
        usuario = request.user
        print("usuario del get_by_notification_id", usuario)

        notificacion_usuario = get_object_or_404(NotificacionUsuario, notificacion=notificacion_id, usuario=usuario)
        return Response({'id': notificacion_usuario.id}, status=status.HTTP_200_OK)
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.usuario != request.user:
            return Response({'error': 'No puedes eliminar notificaciones de otros usuarios'},
                            status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response({'status': 'notificación eliminada'}, status=status.HTTP_200_OK)