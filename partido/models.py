from equipo.models import Equipo

from django.db import models, transaction

from torneo.models import Torneo

from django.db import models


class Partido(models.Model):
    ESTADO_OPCIONES = [
        ('A', 'A jugarse'),
        ('D', 'Disputado'),
        ('E', 'En curso'),
    ]

    equipo_local = models.ForeignKey(Equipo, related_name='partidos_locales', on_delete=models.CASCADE)
    equipo_visitante = models.ForeignKey(Equipo, related_name='partidos_visitantes', on_delete=models.CASCADE)

    equipo_local_goles = models.IntegerField(default=0)
    equipo_visitante_goles = models.IntegerField(default=0)

    fecha = models.DateTimeField(null=True, blank=True)
    torneo = models.ForeignKey(Torneo, on_delete=models.CASCADE, related_name='partidos')
    estado = models.CharField(max_length=1, choices=ESTADO_OPCIONES, default='A')
    diaPartido = models.IntegerField(blank=True, null=True)#Ese atributo tomara valor del api externa
    id_externo = models.IntegerField(blank=True, null=True)#Ese atributo tomara valor del api externa
    estado_anterior = models.CharField(max_length=1, choices=ESTADO_OPCIONES, null=True, blank=True)
    def save(self, *args, **kwargs):
        estado_anterior = None
        if self.pk:  # Si ya existe, obtengo el estado anterior
            estado_anterior = Partido.objects.get(pk=self.pk).estado
        super().save(*args, **kwargs)  # Llamar al método save original

        if estado_anterior != "D" and self.estado == "D":
            self.marcar_como_disputado()

    # Método para marcar el partido como disputado y ajustar acciones
    def marcar_como_disputado(self):
        with transaction.atomic():
            if self.estado == "D":
                # self.estado = "D"
                # self.save()
                # print("El estado ha sido cambiado a 'Disputado'.")

                # Llamar al método de ajuste en los equipos del modelo equipo
                self.equipo_local.ajuste(self.equipo_local, self.equipo_visitante, self.resultado(), self.torneo)
                print("Ajuste de acciones realizado.")

    def resultado(self):
        return self.equipo_local_goles - self.equipo_visitante_goles