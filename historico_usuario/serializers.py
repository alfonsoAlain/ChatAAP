from rest_framework import serializers
from .models import HistoricoUsuario
from historico_equipo.models import HistoricoEquipo
import base64

class HistoricoEquipoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricoEquipo
        fields = ['id', 'equipo', 'fecha', 'precio', 'cantidad']  # Incluye los campos que necesites

class HistoricoUsuarioSerializer(serializers.ModelSerializer):
    nombre_usuario = serializers.CharField(source='usuario.nombre', read_only=True)
    nombre_equipo = serializers.CharField(source='historico_equipo.equipo.nombre', read_only=True)
    escudo_equipo = serializers.SerializerMethodField()
    historico_equipo = HistoricoEquipoSerializer(read_only=True)  # Usa el nuevo serializer

    class Meta:
        model = HistoricoUsuario
        fields = ['id', 'operacion', 'fecha', 'usuario', 'nombre_usuario', 'historico_equipo', 'nombre_equipo', 'escudo_equipo']

    def get_escudo_equipo(self, obj):
        escudo = obj.historico_equipo.equipo.escudo  # Accede al escudo del equipo
        if escudo:  # Asegúrate de que hay una imagen asignada
            with open(escudo.path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                return f"data:image/png;base64,{encoded_string}"  # O el tipo correcto de la imagen
        return None