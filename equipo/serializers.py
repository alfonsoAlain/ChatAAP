import base64

from rest_framework import serializers

from .models import Equipo
from .models import HistorialValorAccion


class EquipoSerializer(serializers.ModelSerializer):
    escudo_base64 = serializers.SerializerMethodField()

    class Meta:
        model = Equipo
        fields = ['id', 'nombre', 'escudo_base64', 'cantidad_acciones', 'valor_inicial_accion',
                  'limite_diario_variacion_precio', 'limite_acciones_jugador']
    def get_escudo_base64(self, obj):
        if obj.escudo:
            with open(obj.escudo.path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return encoded_string
        return None

class HistorialValorAccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistorialValorAccion
        fields = ['fecha', 'valor_accion']

class FootballTeamSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    crestUrl = serializers.URLField()
    shortName = serializers.CharField()
    tla = serializers.CharField()
    address = serializers.CharField()
    website = serializers.URLField()
    founded = serializers.IntegerField()
    clubColors = serializers.CharField()
    venue = serializers.CharField()