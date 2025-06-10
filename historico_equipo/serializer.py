from rest_framework import serializers
from .models import HistoricoEquipo
import base64

class HistoricoEquipoSerializer(serializers.ModelSerializer):
    nombre_equipo = serializers.CharField(source='equipo.nombre', read_only=True)
    escudo_equipo = serializers.SerializerMethodField()

    class Meta:
        model = HistoricoEquipo
        fields = ['id', 'fecha', 'precio', 'cantidad', 'equipo', 'nombre_equipo', 'escudo_equipo']

    def get_escudo_equipo(self, obj):
        if obj.equipo.escudo:  # Asegurarse de que hay una imagen asignada
            with open(obj.equipo.escudo.path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                return f"data:image/png;base64,{encoded_string}"  # O el tipo correcto de la imagen
        return None