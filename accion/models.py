from django.db import models

from equipo.models import Equipo
from usuario.models import Usuario


class Accion(models.Model):
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    cantidad = models.IntegerField()

    def __str__(self):
        return f'Acción de {self.usuario} en {self.equipo} por cantidad {self.cantidad}'
