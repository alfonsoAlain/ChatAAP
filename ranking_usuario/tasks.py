from celery import shared_task
from .models import Usuario, RankingUsuario
from accion.models import Accion
from django.utils import timezone


# Comentario para probar si se actualiza
@shared_task
def calculate_user_ranking():
    fecha_actual = timezone.localdate()

    # Calcular el valor total para cada usuario y almacenarlo en un diccionario
    usuarios_valores = {}
    usuarios = Usuario.objects.filter(is_superuser=False)
    for usuario in usuarios:
        total_valor = _calculate_total_stock_value(usuario)
        usuarios_valores[usuario] = total_valor

    # Ordenar los usuarios por total_valor y seleccionar los 10 mayores
    usuarios_top_10 = sorted(usuarios_valores.items(), key=lambda item: item[1], reverse=True)[:10]

    for usuario, total_valor in usuarios_top_10:
        # Buscar si ya existe un registro para el usuario en la fecha actual
        ranking_usuario, created = RankingUsuario.objects.get_or_create(
            usuario=usuario,
            fecha_calculo__date=fecha_actual,  # Filtrar por la fecha sin la hora
            defaults={'total_valor_acciones': total_valor}
        )

        if not created:  # Si el registro ya existía, actualiza el total
            ranking_usuario.total_valor_acciones = total_valor
            ranking_usuario.save()  # Guardar los cambios

    return "Ranking calculado e insertado/actualizado con éxito."


def _calculate_total_stock_value(usuario):
    acciones = Accion.objects.filter(usuario=usuario)
    total = usuario.cartera.saldo + sum(a.cantidad * a.equipo.valor_inicial_accion for a in acciones)
    return total
