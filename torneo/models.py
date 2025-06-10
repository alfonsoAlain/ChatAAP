from django.db import models

from usuario.models import Usuario

# class Torneo(models.Model):
#     nombre = models.CharField(max_length=255)
#     fechaInicio = models.DateTimeField(null=True, blank=True)
#     fechaFin = models.DateTimeField(null=True, blank=True)
#     jugadores = models.ManyToManyField(Usuario, related_name='torneos')
#
#     def __str__(self):
#         return self.nombre

class Torneo(models.Model):
    TIPO_TORNEO_OPCIONES = [
        ('A', 'Amistoso'),
        ('L', 'Local'),
        ('I', 'Internacional'),
    ]

    nombre = models.CharField(max_length=255)
    fechaInicio = models.DateTimeField(null=True, blank=True)
    fechaFin = models.DateTimeField(null=True, blank=True)
    jugadores = models.ManyToManyField(Usuario, related_name='torneos')
    tipo = models.CharField(max_length=1, choices=TIPO_TORNEO_OPCIONES, default='A')
    id_externo = models.IntegerField(blank=True, null=True)#Este atributo tomara valor del api externa
    jornada_actual_externo = models.IntegerField(blank=True, null=True)#Este atributo tomara valor del api externa
    codigo_externo = models.CharField(max_length=6, null=True, blank=True)#Este atributo tomara valor del api externa
    def __str__(self):
        return self.nombre