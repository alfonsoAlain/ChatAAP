import requests
from django.db import transaction
from django.forms import models
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import viewsets, status, serializers
from rest_framework.views import APIView

from equipo.models import Equipo
from partido.serializers import PartidoSerializer
from torneo.models import Torneo
from .models import Partido


class CustomPagination(PageNumberPagination):
    # Clase de paginación personalizada
    page_size_query_param = 'page_size'  # Nombre del parámetro que se usará
    max_page_size = 100  # Número máximo de registros que se pueden solicitar por página


class PartidoViewSet(viewsets.ModelViewSet):
    queryset = Partido.objects.all()
    serializer_class = PartidoSerializer
    pagination_class = CustomPagination  # Asigna la clase de paginación personalizada

    def get_queryset(self):
        # Obtener el queryset base
        queryset = super().get_queryset()

        # Diccionario para los filtros
        filtros = {}

        # Obtener parámetros para la consulta
        dia_partido = self.request.query_params.get('diaPartido', None)
        torneo_id = self.request.query_params.get('torneo', None)
        estado = self.request.query_params.get('estado', None)

        # Añadir filtros al diccionario si se envian parámetros
        if dia_partido:
            filtros['diaPartido'] = dia_partido

        if torneo_id:
            filtros['torneo_id'] = torneo_id

        if estado:
            filtros['estado'] = estado

        if filtros:
            queryset = queryset.filter(**filtros)

        return queryset

    def perform_update(self, serializer):
        instance = serializer.save()  # Guarda la instancia
        print(f"Partido actualizado: {instance.id}, Estado actual: {instance.estado}")

        if instance.estado != "D":
            print("Llamando a marcar_como_disputado()")
            instance.marcar_como_disputado()
        else:
            print("El partido ya está disputado.")


class FootballMatchesAPIView(APIView):
    def post(self, request):
        try:
            with transaction.atomic():  # Inicia la transacción atómica
                # Obtener el código de la liga del cuerpo de la solicitud
                liga_codigo = request.data.get('liga_codigo', 'PD')  # Valor por defecto 'PD' si no se proporciona

                # Hacer la solicitud a la API de football-data.org
                url = f'https://api.football-data.org/v4/competitions/{liga_codigo}/matches'

                headers = {'X-Auth-Token': '89a8b518af074e6bb98f14de3ad9bbae'}
                response = requests.get(url, headers=headers)

                if response.status_code != 200:
                    return Response({"error": "Error al obtener los datos"}, status=status.HTTP_400_BAD_REQUEST)

                # Procesar los datos recibidos
                competition = response.json().get('competition', {})
                id_competition = competition.get('id')
                torneo = Torneo.objects.get(id_externo=id_competition)

                if not torneo:
                    raise serializers.ValidationError("Debe agregar local no existe.")

                matches = response.json().get('matches', [])
                partidos_insertados = 0

                # Mapeo de estados
                estado_map = {
                    'SCHEDULED': 'A',  # A jugarse
                    'TIMED': 'A',  # A jugarse
                    'FINISHED': 'D',  # Disputado
                    'IN_PLAY': 'E'  # En curso
                }

                # Iterar sobre cada equipo y crear instancias en la base de datos
                for match in matches:
                    # Extraer información relevante
                    liga_nombre = match.get('competition', {}).get('name')
                    fecha = match.get('utcDate')
                    id_externo_home_team = match.get('homeTeam', {}).get('id')
                    equipo_local = Equipo.objects.get(id_externo=id_externo_home_team)

                    if not equipo_local:
                        raise serializers.ValidationError("El equipo local no existe.")

                    id_externo_away_team = match.get('awayTeam', {}).get('id')
                    equipo_visitante = Equipo.objects.get(id_externo=id_externo_away_team)

                    if not equipo_visitante:
                        raise serializers.ValidationError("El equipo visitante no existe.")

                    equipo_local_goles = match.get('score', {}).get('fullTime', {}).get('home')
                    equipo_visitante_goles = match.get('score', {}).get('fullTime', {}).get('away')
                    # Asignar 0 si los goles son None
                    equipo_local_goles = equipo_local_goles if equipo_local_goles is not None else 0
                    equipo_visitante_goles = equipo_visitante_goles if equipo_visitante_goles is not None else 0

                    id_externo_torneo = match.get('competition', {}).get('id')
                    torneo = Torneo.objects.get(id_externo=id_externo_torneo)

                    if not torneo:
                        raise serializers.ValidationError("El torneo no existe.")

                    # Asigna el estado del partido basado en el mapeo
                    estado = estado_map.get(match.get('status'), 'A')  # Por defecto a 'A'

                    diaPartido = match.get('matchday')
                    id_externo = match.get('id')

                    # Verificar si el partido ya existe en la base de datos
                    if not Partido.objects.filter(id_externo=id_externo).exists():
                        # Crear un nuevo objeto Equipo
                        partido = Partido(
                            fecha=fecha,
                            equipo_local=equipo_local,
                            equipo_visitante=equipo_visitante,
                            equipo_local_goles=equipo_local_goles,
                            equipo_visitante_goles=equipo_visitante_goles,
                            estado=estado,
                            torneo=torneo,
                            diaPartido=diaPartido,
                            id_externo=id_externo
                        )

                        # Guardar el equipo en la base de datos
                        partido.save()
                        partidos_insertados += 1

                if partidos_insertados > 0:
                    return Response({
                        "message": f"{partidos_insertados} partidos de la liga {liga_nombre} insertados correctamente"},
                        status=status.HTTP_201_CREATED)
                else:
                    return Response({"message": "No se insertó ningún partido, pues ya estaban insertados"},
                                    status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            raise serializers.ValidationError(e)


class FootballUpdateMatchesStatusAPIView(APIView):
    def post(self, request):
        try:
            with transaction.atomic():

                # Obtener el código de la liga del cuerpo de la solicitud
                lista_codigo_liga = request.data.get('lista_codigo_liga')
                lista_codigo_partido = request.data.get('liga_codigo_partido')

                # Lista para almacenar los resultados de las solicitudes
                resultados = []
                partidos_actualizados = 0

                # Recorre cada torneo y obtiene el codigo_externo
                for codigo_liga in lista_codigo_liga:

                    # Realiza la solicitud a la API
                    # url = 'http://127.0.0.1:8000/api/v1/partidos/obtener/football-matches/'
                    url = f'https://api.football-data.org/v4/competitions/{codigo_liga}/matches/?status=IN_PLAY'
                    headers = {'X-Auth-Token': '89a8b518af074e6bb98f14de3ad9bbae'}
                    response = requests.get(url, headers=headers)

                    if response.status_code == 200:
                        # Agrega la respuesta a la lista de resultados
                        # resultados.append(response.json())
                        matches = response.json().get('matches', [])
                        # Recorro la lista de ids de partidos que llegan del frontend

                        for codigo_partido in lista_codigo_partido:
                            # Recorro la lista de partidos que devolvio el endpoint
                            for match in matches:
                                if codigo_partido == match.get('id'):

                                    partido = Partido.objects.get(id=codigo_partido)

                                    if not partido:
                                        raise serializers.ValidationError(f"El partido con id {codigo_partido}, no existe.")

                                    match_estado = match.get('status')
                                    match_local_goles = match.get('score', {}).get('fullTime', {}).get('home')
                                    match_visitante_goles = match.get('score', {}).get('fullTime', {}).get('away')

                                    if match_estado == "FINISHED":

                                        partido.estado = 'D'
                                        partido.equipo_local_goles = match_local_goles
                                        partido.equipo_visitante_goles = match_visitante_goles
                                        partido.save()
                                        partidos_actualizados += 1

                                    else:
                                        if partido.equipo_local_goles != match_local_goles or \
                                                partido.equipo_visitante_goles != match_visitante_goles:
                                            partido.equipo_local_goles = match_local_goles
                                            partido.equipo_visitante_goles = match_visitante_goles
                                            partido.save()
                                            partidos_actualizados += 1

                    else: # Cuando no se encuentra un partido en juego para ese torneo

                        lista_partidos = Partido.objects.filter(
                            (models.Q(equipo_local__liga_base=codigo_liga) | models.Q(
                                equipo_visitante__liga_base=codigo_liga)),
                            estado_anterior='E'
                        )
                        for partido in lista_partidos:

                            url = f'https://api.football-data.org/v4/competitions/{codigo_liga}/matches/?status=FINISHED'
                            headers = {'X-Auth-Token': '89a8b518af074e6bb98f14de3ad9bbae'}
                            response = requests.get(url, headers=headers)

                            if response.status_code == 200:
                                matches = response.json().get('matches', [])

                                for match in matches:
                                    if partido.id == match.get('id'):
                                        match_local_goles = match.get('score', {}).get('fullTime', {}).get('home')
                                        match_visitante_goles = match.get('score', {}).get('fullTime', {}).get('away')
                                        partido.equipo_local_goles = match_local_goles
                                        partido.equipo_visitante_goles = match_visitante_goles
                                        partido.estado = 'D'

                                        partido.save()
                                        partidos_actualizados += 1

                if partidos_actualizados > 0:
                    return Response({
                        "message": f"{partidos_actualizados} partidos actualizados"},
                        status=status.HTTP_200_OK)
                else:
                    return Response({"message": "No se actualizó ningún partido, pues no hubo cambios"},
                                    status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            raise serializers.ValidationError(e)


class MatchDetailView(APIView):
    def get(self, request):
        data = {
            "filters": {
                "season": "2021",
                "matchday": "34"
            },
            "resultSet": {
                "count": 9,
                "first": "2022-05-14",
                "last": "2022-05-14",
                "played": 9
            },
            "competition": {
                "id": 2002,
                "name": "Bundesliga",
                "code": "BL1",
                "type": "LEAGUE",
                "emblem": "https://crests.football-data.org/BL1.png"
            },
            "matches": [
                {
                    "area": {
                        "id": 2088,
                        "name": "Germany",
                        "code": "DEU",
                        "flag": "https://crests.football-data.org/759.svg"
                    },
                    "competition": {
                        "id": 2002,
                        "name": "Bundesliga",
                        "code": "BL1",
                        "type": "LEAGUE",
                        "emblem": "https://crests.football-data.org/BL1.png"
                    },
                    "season": {
                        "id": 742,
                        "startDate": "2021-08-13",
                        "endDate": "2022-05-14",
                        "currentMatchday": 34,
                        "winner": "null",
                        "stages": [
                            "REGULAR_SEASON"
                        ]
                    },
                    "id": 1437,
                    "utcDate": "2022-05-14T13:30:00Z",
                    "status": "FINISHED",
                    "minute": "90",
                    "injuryTime": 5,
                    "attendance": "null",
                    "venue": "Signal Iduna Park",
                    "matchday": 34,
                    "stage": "REGULAR_SEASON",
                    "group": "null",
                    "lastUpdated": "2022-05-15T03:33:01Z",
                    "homeTeam": {
                        "id": 4,
                        "name": "Borussia Dortmund",
                        "shortName": "Dortmund",
                        "tla": "BVB",
                        "crest": "https://crests.football-data.org/4.png",
                        "coach": {
                            "id": 15111,
                            "name": "Marco Rose",
                            "nationality": "Germany"
                        },
                        "leagueRank": 2,
                        "formation": "3-4-2-1",
                        "lineup": [],
                        "bench": []
                    },
                    "awayTeam": {
                        "id": 9,
                        "name": "Hertha BSC",
                        "shortName": "Hertha BSC",
                        "tla": "BSC",
                        "crest": "https://crests.football-data.org/9.svg",
                        "coach": {
                            "id": 156101,
                            "name": "Felix Magath",
                            "nationality": "Germany"
                        },
                        "leagueRank": 15,
                        "formation": "4-2-3-1",
                        "lineup": [],
                        "bench": []
                    },
                    "score": {
                        "winner": "HOME_TEAM",
                        "duration": "REGULAR",
                        "fullTime": {
                            "home": 2,
                            "away": 1
                        },
                        "halfTime": {
                            "home": 0,
                            "away": 1
                        }
                    },
                    "goals": [
                        {
                            "minute": 18,
                            "injuryTime": "null",
                            "type": "PENALTY",
                            "team": {
                                "id": 9,
                                "name": "Hertha BSC"
                            },
                            "scorer": {
                                "id": 9466,
                                "name": "Ishak Belfodil"
                            },
                            "assist": "null",
                            "score": {
                                "home": 0,
                                "away": 1
                            }
                        },
                        {
                            "minute": 68,
                            "injuryTime": "null",
                            "type": "PENALTY",
                            "team": {
                                "id": 4,
                                "name": "Borussia Dortmund"
                            },
                            "scorer": {
                                "id": 38101,
                                "name": "Erling Haaland"
                            },
                            "assist": "null",
                            "score": {
                                "home": 1,
                                "away": 1
                            }
                        },
                        {
                            "minute": 84,
                            "injuryTime": "null",
                            "type": "REGULAR",
                            "team": {
                                "id": 4,
                                "name": "Borussia Dortmund"
                            },
                            "scorer": {
                                "id": 150817,
                                "name": "Youssoufa Moukoko"
                            },
                            "assist": {
                                "id": 125010,
                                "name": "Jude Bellingham"
                            },
                            "score": {
                                "home": 2,
                                "away": 1
                            }
                        }
                    ],
                    "penalties": [
                        {
                            "player": {
                                "id": 9466,
                                "name": "Ishak Belfodil"
                            },
                            "team": {
                                "id": 9,
                                "name": "Hertha BSC"
                            },
                            "scored": "true"
                        },
                        {
                            "player": {
                                "id": 38101,
                                "name": "Erling Haaland"
                            },
                            "team": {
                                "id": 4,
                                "name": "Borussia Dortmund"
                            },
                            "scored": "true"
                        }
                    ],
                    "bookings": [],
                    "substitutions": [],
                    "odds": {
                        "homeWin": 1.3,
                        "draw": 6.08,
                        "awayWin": 8.36
                    },
                    "referees": [
                        {
                            "id": 15747,
                            "name": "Christian Gittelmann",
                            "type": "ASSISTANT_REFEREE_N1",
                            "nationality": "Germany"
                        },
                        {
                            "id": 8827,
                            "name": "Eduard Beitinger",
                            "type": "ASSISTANT_REFEREE_N2",
                            "nationality": "Germany"
                        },
                        {
                            "id": 57532,
                            "name": "Frank Willenborg",
                            "type": "FOURTH_OFFICIAL",
                            "nationality": "Germany"
                        },
                        {
                            "id": 43943,
                            "name": "Tobias Stieler",
                            "type": "REFEREE",
                            "nationality": "Germany"
                        },
                        {
                            "id": 43922,
                            "name": "Benjamin Brand",
                            "type": "VIDEO_ASSISTANT_REFEREE_N1",
                            "nationality": "Germany"
                        },
                        {
                            "id": 57678,
                            "name": "Philipp Hüwe",
                            "type": "VIDEO_ASSISTANT_REFEREE_N2",
                            "nationality": "Germany"
                        }
                    ]
                },
                {
                    "area": {
                        "id": 2088,
                        "name": "Germany",
                        "code": "DEU",
                        "flag": "https://crests.football-data.org/759.svg"
                    },
                    "competition": {
                        "id": 2002,
                        "name": "Bundesliga",
                        "code": "BL1",
                        "type": "LEAGUE",
                        "emblem": "https://crests.football-data.org/BL1.png"
                    },
                    "season": {
                        "id": 742,
                        "startDate": "2021-08-13",
                        "endDate": "2022-05-14",
                        "currentMatchday": 34,
                        "winner": "null",
                        "stages": [
                            "REGULAR_SEASON"
                        ]
                    },
                    "id": 1817,
                    "utcDate": "2022-05-14T13:30:00Z",
                    "status": "FINISHED",
                    "minute": "90",
                    "injuryTime": 5,
                    "attendance": "null",
                    "venue": "Signal Iduna Park",
                    "matchday": 34,
                    "stage": "REGULAR_SEASON",
                    "group": "null",
                    "lastUpdated": "2022-05-15T03:33:01Z",
                    "homeTeam": {
                        "id": 4,
                        "name": "Borussia Dortmund",
                        "shortName": "Dortmund",
                        "tla": "BVB",
                        "crest": "https://crests.football-data.org/4.png",
                        "coach": {
                            "id": 15111,
                            "name": "Marco Rose",
                            "nationality": "Germany"
                        },
                        "leagueRank": 2,
                        "formation": "3-4-2-1",
                        "lineup": [],
                        "bench": []
                    },
                    "awayTeam": {
                        "id": 9,
                        "name": "Hertha BSC",
                        "shortName": "Hertha BSC",
                        "tla": "BSC",
                        "crest": "https://crests.football-data.org/9.svg",
                        "coach": {
                            "id": 156101,
                            "name": "Felix Magath",
                            "nationality": "Germany"
                        },
                        "leagueRank": 15,
                        "formation": "4-2-3-1",
                        "lineup": [],
                        "bench": []
                    },
                    "score": {
                        "winner": "HOME_TEAM",
                        "duration": "REGULAR",
                        "fullTime": {
                            "home": 2,
                            "away": 1
                        },
                        "halfTime": {
                            "home": 0,
                            "away": 1
                        }
                    },
                    "goals": [
                        {
                            "minute": 18,
                            "injuryTime": "null",
                            "type": "PENALTY",
                            "team": {
                                "id": 9,
                                "name": "Hertha BSC"
                            },
                            "scorer": {
                                "id": 9466,
                                "name": "Ishak Belfodil"
                            },
                            "assist": "null",
                            "score": {
                                "home": 0,
                                "away": 1
                            }
                        },
                        {
                            "minute": 68,
                            "injuryTime": "null",
                            "type": "PENALTY",
                            "team": {
                                "id": 4,
                                "name": "Borussia Dortmund"
                            },
                            "scorer": {
                                "id": 38101,
                                "name": "Erling Haaland"
                            },
                            "assist": "null",
                            "score": {
                                "home": 1,
                                "away": 1
                            }
                        },
                        {
                            "minute": 84,
                            "injuryTime": "null",
                            "type": "REGULAR",
                            "team": {
                                "id": 4,
                                "name": "Borussia Dortmund"
                            },
                            "scorer": {
                                "id": 150817,
                                "name": "Youssoufa Moukoko"
                            },
                            "assist": {
                                "id": 125010,
                                "name": "Jude Bellingham"
                            },
                            "score": {
                                "home": 2,
                                "away": 1
                            }
                        }
                    ],
                    "penalties": [
                        {
                            "player": {
                                "id": 9466,
                                "name": "Ishak Belfodil"
                            },
                            "team": {
                                "id": 9,
                                "name": "Hertha BSC"
                            },
                            "scored": "true"
                        },
                        {
                            "player": {
                                "id": 38101,
                                "name": "Erling Haaland"
                            },
                            "team": {
                                "id": 4,
                                "name": "Borussia Dortmund"
                            },
                            "scored": "true"
                        }
                    ],
                    "bookings": [],
                    "substitutions": [],
                    "odds": {
                        "homeWin": 1.3,
                        "draw": 6.08,
                        "awayWin": 8.36
                    },
                    "referees": [
                        {
                            "id": 15747,
                            "name": "Christian Gittelmann",
                            "type": "ASSISTANT_REFEREE_N1",
                            "nationality": "Germany"
                        },
                        {
                            "id": 8827,
                            "name": "Eduard Beitinger",
                            "type": "ASSISTANT_REFEREE_N2",
                            "nationality": "Germany"
                        },
                        {
                            "id": 57532,
                            "name": "Frank Willenborg",
                            "type": "FOURTH_OFFICIAL",
                            "nationality": "Germany"
                        },
                        {
                            "id": 43943,
                            "name": "Tobias Stieler",
                            "type": "REFEREE",
                            "nationality": "Germany"
                        },
                        {
                            "id": 43922,
                            "name": "Benjamin Brand",
                            "type": "VIDEO_ASSISTANT_REFEREE_N1",
                            "nationality": "Germany"
                        },
                        {
                            "id": 57678,
                            "name": "Philipp Hüwe",
                            "type": "VIDEO_ASSISTANT_REFEREE_N2",
                            "nationality": "Germany"
                        }
                    ]
                }
            ]
        }

        return Response(data,
                        status=status.HTTP_200_OK)
