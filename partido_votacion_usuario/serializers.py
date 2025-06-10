from rest_framework import serializers
from .models import PartidoVotacionUsuario

class PartidoVotacionUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartidoVotacionUsuario
        fields = '__all__'