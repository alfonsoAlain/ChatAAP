import base64
from rest_framework import serializers
from partido.models import Partido


class PartidoSerializer(serializers.ModelSerializer):
    equipo_local_nombre = serializers.CharField(source='equipo_local.nombre', read_only=True)
    equipo_visitante_nombre = serializers.CharField(source='equipo_visitante.nombre', read_only=True)
    equipo_local_escudo = serializers.SerializerMethodField()
    equipo_visitante_escudo = serializers.SerializerMethodField()
    resultado = serializers.SerializerMethodField()  # Nuevo campo resultado
    liga_base = serializers.SerializerMethodField()

    class Meta:
        model = Partido
        fields = '__all__'

    def validate(self, data):
        if data['equipo_local'] == data['equipo_visitante']:
            raise serializers.ValidationError("El equipo local y visitante deben ser diferentes.")
        return data

    def get_equipo_local_escudo(self, obj):
        # Codificar el escudo local en Base64
        if obj.equipo_local.escudo:
            with open(obj.equipo_local.escudo.path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                return encoded_string
        return None

    def get_equipo_visitante_escudo(self, obj):
        # Codificar el escudo visitante en Base64
        if obj.equipo_visitante.escudo:
            with open(obj.equipo_visitante.escudo.path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                return encoded_string
        return None

    def get_resultado(self, obj):
        # Combinar los goles de los equipos
        return f"{obj.equipo_local_goles}-{obj.equipo_visitante_goles}"

    def get_liga_base(self, obj):

        return f"{obj.equipo_local.liga_base}"

    def update(self, instance, validated_data):
        estado_anterior = instance.estado  # Guarda el estado anterior
        instance = super().update(instance, validated_data)  # Actualiza el partido

        # Si el estado pasó a "Disputado", realiza el ajuste de acciones
        if estado_anterior != "D" and instance.estado == "D":
            instance.marcar_como_disputado()

        return instance
