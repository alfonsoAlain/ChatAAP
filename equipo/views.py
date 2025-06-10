import requests
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework import viewsets, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Equipo, HistorialValorAccion
from .serializers import EquipoSerializer, HistorialValorAccionSerializer, FootballTeamSerializer


class CustomPagination(PageNumberPagination):
    # Clase de paginación personalizada
    page_size_query_param = 'page_size'  # Nombre del parámetro que se usará
    max_page_size = 100  # Número máximo de registros que se pueden solicitar por página


class EquipoViewSet(viewsets.ModelViewSet):
    queryset = Equipo.objects.all()
    serializer_class = EquipoSerializer
    pagination_class = CustomPagination

class HistoricoAccionEquipoViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = HistorialValorAccionSerializer

    def get_queryset(self):
        equipo_id = self.kwargs['equipo_id']
        return HistorialValorAccion.objects.filter(equipo_id=equipo_id)


class FootballTeamsAPIView(APIView):
    def post(self, request):
        # Obtener el código de la liga del cuerpo de la solicitud
        liga_codigo = request.data.get('liga_codigo', 'PD')  # Valor por defecto 'PD' si no se proporciona

        # Hacer la solicitud a la API de football-data.org
        url = f'https://api.football-data.org/v4/competitions/{liga_codigo}/teams'
        headers = {'X-Auth-Token': '89a8b518af074e6bb98f14de3ad9bbae'}
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return Response({"error": "Error al obtener los datos"}, status=status.HTTP_400_BAD_REQUEST)

            # Procesar los datos recibidos
        teams = response.json().get('teams', [])
        equipos_insertados = 0

        # Iterar sobre cada equipo y crear instancias en la base de datos
        for team in teams:
            # Extraer información relevante
            nombre = team.get('name')
            escudo_url = team.get('crest')  # Usamos el link del escudo
            cantidad_acciones = 1000  # Valor default
            valor_inicial_accion = 10.00  # Valor default
            limite_diario_variacion_precio = 5.00  # Valor default
            limite_acciones_jugador = 100  # Valor default
            liga_base = team.get('area', {}).get('code')  # 'ESP' para La Liga
            liga_nombre = team.get('area', {}).get('name')
            id_externo = team.get('id')
            short_name = team.get('shortName')

            # Verificar si el equipo ya existe en la base de datos
            if not Equipo.objects.filter(id_externo=id_externo).exists():
                escudo = guardar_imagen(id_externo, short_name, escudo_url)
                # Crear un nuevo objeto Equipo
                equipo = Equipo(
                    nombre=nombre,
                    escudo=escudo,
                    cantidad_acciones=cantidad_acciones,
                    valor_inicial_accion=valor_inicial_accion,
                    limite_diario_variacion_precio=limite_diario_variacion_precio,
                    limite_acciones_jugador=limite_acciones_jugador,
                    liga_base=liga_base,
                    id_externo=id_externo
                )

                # Guardar el equipo en la base de datos
                equipo.save()
                equipos_insertados += 1

        if equipos_insertados > 0:
            return Response({"message": f"{equipos_insertados} equipos de la liga {liga_nombre} insertados correctamente"},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "No se insertó ningún equipo, pues ya estaban insertados"},
                            status=status.HTTP_204_NO_CONTENT)

def guardar_imagen(id_externo, short_name, url_imagen):
    try:
        # Realizar la solicitud GET para descargar la imagen
        response = requests.get(url_imagen)
        response.raise_for_status()  # Lanza un error si la respuesta no es exitosa

        # Crear un nombre de archivo único basado en id_externo
        extension = url_imagen.split('.')[-1]  # Obtener la extensión de la imagen
        nombre_archivo = f'escudos/{id_externo}_{short_name}.{extension}'  # Nombre del archivo

        # Guardar la imagen en el sistema de archivos de Django
        default_storage.save(nombre_archivo, ContentFile(response.content))

        # Devolver la ruta del archivo guardado
        return nombre_archivo
    except Exception as e:
        # Manejo de errores (opcional)
        print(f"Error al guardar la imagen: {e}")
        return None