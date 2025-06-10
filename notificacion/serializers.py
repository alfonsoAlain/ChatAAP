from rest_framework import serializers

from .models import Notificacion, NotificacionUsuario


class NotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacion
        fields = ['id', 'titulo', 'mensaje', 'tipo', 'fechaInicio', 'fechaFin']


class NotificacionUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificacionUsuario
        fields = '__all__'
