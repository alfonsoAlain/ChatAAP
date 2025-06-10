from rest_framework import serializers
from .models import Torneo
from usuario.models import Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'username']


class TorneoSerializer(serializers.ModelSerializer):
    jugadores = UsuarioSerializer(many=True, read_only=True)

    class Meta:
        model = Torneo
        fields = '__all__'
