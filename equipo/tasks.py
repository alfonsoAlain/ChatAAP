from collections import defaultdict

from celery import shared_task


from django.db.models import Sum, F
from historico_equipo.models import HistoricoEquipo
from equipo.models import Equipo, HistorialValorAccion


@shared_task
def actualizar_valor_inicial_accion():

    historicos = (
        HistoricoEquipo.objects
        .order_by('-fecha')
        .values('equipo')
        .annotate(
            total_precio=Sum(F('precio') * F('cantidad')),
            total_cantidad=Sum('cantidad')
        )
    )

    # Creo un diccionario para almacenar los últimos 5 registros por equipo
    equipos_registros = defaultdict(list)


    for registro in historicos:
        equipo_id = registro['equipo']
        equipos_registros[equipo_id].append(registro)

        # Calcular totals
    total_acumulado_precio = {}
    total_acumulado_cantidad = {}

    for equipo_id, registros in equipos_registros.items():
        for historico in registros[:5]:  # Solo tomar los últimos 5 registros
            total_precio = historico['total_precio']
            total_cantidad = historico['total_cantidad']

            if equipo_id not in total_acumulado_precio:
                total_acumulado_precio[equipo_id] = 0
                total_acumulado_cantidad[equipo_id] = 0


            total_acumulado_precio[equipo_id] += total_precio
            total_acumulado_cantidad[equipo_id] += total_cantidad

    for equipo_id in total_acumulado_precio:
        if total_acumulado_cantidad[equipo_id] > 0:  # Evitar división por cero
            promedio_ponderado = total_acumulado_precio[equipo_id] / total_acumulado_cantidad[equipo_id]
            # Actualizar el valor_inicial_accion del equipo correspondiente

            Equipo.objects.filter(id=equipo_id).update(valor_inicial_accion=promedio_ponderado)
            equipo = Equipo.objects.get(id=equipo_id)
            nuevo_valor = HistorialValorAccion(equipo=equipo, valor_accion=promedio_ponderado)
            nuevo_valor.save()

    #Agregar registros para los equipos que no tienen historial
    equipos_sin_historial = Equipo.objects.exclude(id__in=equipos_registros.keys())
    for equipo in equipos_sin_historial:
        nuevo_valor = HistorialValorAccion(equipo=equipo, valor_accion=equipo.valor_inicial_accion)
        nuevo_valor.save()

    return "Valores de las acciones actualizados correctamente."
