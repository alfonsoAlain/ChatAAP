from django.utils import timezone
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from accion.models import Accion
from ranking_usuario.models import RankingUsuario
from ranking_usuario.serializers import RankingUsuarioSerializer
from usuario.models import Usuario
from django.db.models import DateField, functions


class RankingUsuarioListView(generics.ListAPIView):
    serializer_class = RankingUsuarioSerializer

    def get_queryset(self):
        fecha = self.request.query_params.get('fecha', None)
        if fecha:
            fecha_datetime = timezone.make_aware(timezone.datetime.strptime(fecha, '%Y-%m-%d'))
            return RankingUsuario.objects.filter(fecha_calculo__date=fecha_datetime.date()).order_by(
                '-total_valor_acciones')
        else:
            return RankingUsuario.objects.all().order_by('-total_valor_acciones')


class UsuarioRankingCreateView(generics.CreateAPIView):
    queryset = Usuario.objects.all()  # Se puede usar para otras operaciones si es necesario
    serializer_class = RankingUsuarioSerializer

    def create(self, request, *args, **kwargs):
        # Obtener todos los usuarios y calcular el total_valor_acciones
        usuarios = Usuario.objects.all()
        for usuario in usuarios:
            total_valor = self.calcular_valor_acciones(usuario)
            # Guardar el ranking de cada usuario
            RankingUsuario.objects.update_or_create(
                usuario=usuario,
                defaults={'total_valor_acciones': total_valor}
            )
        return Response({"message": "Ranking calculado e insertado con éxito."}, status=201)

    def calcular_valor_acciones(self, usuario):
        acciones = Accion.objects.filter(usuario=usuario)
        total = usuario.cartera.saldo + sum(a.cantidad * a.equipo.valor_inicial_accion for a in acciones)
        return total


class RankingUsuarioFechaView(APIView):
    def get(self, request):
        # Obtener las fechas únicas de fecha_calculo
        fechas_unicas = RankingUsuario.objects.annotate(
            fecha_calculo_date=functions.Trunc('fecha_calculo', 'day', output_field=DateField())
        ).values('fecha_calculo_date').distinct().order_by('-fecha_calculo_date')

        # Preparar la respuesta
        data = [{'fecha_calculo': fecha['fecha_calculo_date']} for fecha in fechas_unicas]

        return Response(data)
