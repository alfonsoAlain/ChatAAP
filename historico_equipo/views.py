import base64

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import HistoricoEquipo
from rest_framework import status
from .serializer import HistoricoEquipoSerializer

class HistoricoEquipoViewSet(viewsets.ModelViewSet):
    serializer_class = HistoricoEquipoSerializer

    def get_queryset(self):
        equipo_id = self.kwargs.get('equipo_id')
        if equipo_id:
            return HistoricoEquipo.objects.filter(equipo_id=equipo_id)  # Filtra por el ID del equipo
        return HistoricoEquipo.objects.all()  # Devuelve todo si no hay ID

    def list(self, request, *args, **kwargs):
        # Llamar a 'get_queryset' para obtener el queryset filtrado
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# class DiferenciaPrecioAPIView(APIView):
#     def get(self, request):
#         # Obtener todos los históricos de equipos, ordenados por fecha
#         historicos = HistoricoEquipo.objects.all().order_by('equipo', '-fecha')
#
#         resultado = []
#
#         # Agrupar los históricos por equipo
#         equipos = {}
#         for historico in historicos:
#             if historico.equipo.id not in equipos:
#                 equipos[historico.equipo.id] = []
#             equipos[historico.equipo.id].append(historico)
#
#             # Calcular la diferencia de precio para los dos últimos registros de cada equipo
#         for equipo_id, registros in equipos.items():
#             if len(registros) >= 2:
#                 # Obtener los dos últimos registros
#                 ultimo_registro = registros[0]
#                 penultimo_registro = registros[1]
#
#                 # Calcular la diferencia de precios
#                 diferencia_precio = ultimo_registro.precio - penultimo_registro.precio
#
#                 # Agregar el resultado a la lista
#                 resultado.append({
#                     'equipo': ultimo_registro.equipo.nombre,
#                     'ultimo_precio': ultimo_registro.precio,
#                     'penultimo_precio': penultimo_registro.precio,
#                     'diferencia_precio': diferencia_precio,
#                     'fecha_ultimo': ultimo_registro.fecha,
#                     'fecha_penultimo': penultimo_registro.fecha
#                 })
#
#         return Response(resultado, status=status.HTTP_200_OK)

class DiferenciaPrecioAPIView(APIView):
    def get(self, request):
        # Obtener todos los históricos de equipos, ordenados por fecha
        historicos = HistoricoEquipo.objects.all().order_by('equipo', '-fecha')

        resultado = []

        # Agrupar los históricos por equipo
        equipos = {}
        for historico in historicos:
            if historico.equipo.id not in equipos:
                equipos[historico.equipo.id] = []
            equipos[historico.equipo.id].append(historico)

        # Calcular la diferencia de precio para los dos últimos registros de cada equipo
        for equipo_id, registros in equipos.items():
            if len(registros) >= 2:
                # Obtener los dos últimos registros
                ultimo_registro = registros[0]
                penultimo_registro = registros[1]

                # Calcular la diferencia de precios
                diferencia_precio = ultimo_registro.precio - penultimo_registro.precio

                # Obtener el escudo del equipo en formato Base64
                escudo = ultimo_registro.equipo.escudo
                escudo_base64 = ''
                if escudo:  # Verificar si el escudo existe
                    try:
                        with escudo.open('rb') as image_file:
                            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                            escudo_base64 = f"data:image/jpeg;base64,{encoded_string}"  # Ajusta el tipo MIME según sea necesario
                    except Exception:
                        escudo_base64 = ''  # Si ocurre un error al leer, devolver vacío

                resultado.append({
                    'id': ultimo_registro.id,
                    'id_equipo': ultimo_registro.equipo.id,
                    'equipo': ultimo_registro.equipo.nombre,
                    'diferencia_precio': diferencia_precio,
                    'precio_actual': ultimo_registro.precio,
                    'escudo': escudo_base64,
                })


                # Separar equipos en mejores y peores
        #mejores_equipos = sorted([r for r in resultado if r['diferencia_precio'] > 0],
        #                          key=lambda x: x['diferencia_precio'], reverse=True)[:5]
        #peores_equipos = sorted([r for r in resultado if r['diferencia_precio'] <= 0],
        #                        key=lambda x: x['diferencia_precio'])[:5]

        mejores_equipos = sorted(resultado, key=lambda x: x['diferencia_precio'], reverse=True)

        return Response({
            'mejores_equipos': mejores_equipos,
        }, status=status.HTTP_200_OK)
