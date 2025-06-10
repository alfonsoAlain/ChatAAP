from rest_framework import serializers
from .models import RankingUsuario


class RankingUsuarioSerializer(serializers.ModelSerializer):
    nombre_usuario = serializers.CharField(source='usuario.username', read_only=True)
    nombre = serializers.CharField(source='usuario.nombre', read_only=True)
    correo = serializers.CharField(source='usuario.email', read_only=True)
    apellido = serializers.CharField(source='usuario.apellido', read_only=True)
    fecha_calculo = serializers.DateTimeField()

    class Meta:
        model = RankingUsuario
        fields = ['id', 'nombre_usuario', 'nombre', 'apellido', 'correo', 'total_valor_acciones', 'fecha_calculo']
