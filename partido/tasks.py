import requests
from celery import shared_task

from torneo.models import Torneo


@shared_task
def actualizar_valores_partidos():
    # Obtiene todos los torneos
    torneos = Torneo.objects.all()

    # Lista para almacenar los resultados de las solicitudes
    resultados = []

    # Recorre cada torneo y obtiene el codigo_externo
    for torneo in torneos:
        codigo_externo = torneo.codigo_externo
        if codigo_externo:  # Verifica que el codigo_externo no sea None
            # Realiza la solicitud a la API
            url = f'https://api.football-data.org/v4/competitions/{codigo_externo}/matches/?status=IN_PLAY'
            headers = {'X-Auth-Token': '89a8b518af074e6bb98f14de3ad9bbae'}
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                # Agrega la respuesta a la lista de resultados
                resultados.append(response.json())
            else:
                # Manejar el caso de error en la solicitud
                resultados.append({
                    'codigo_externo': codigo_externo,
                    'error': response.status_code,
                    'mensaje': response.text
                })


    return "Valores de las acciones actualizados correctamente."