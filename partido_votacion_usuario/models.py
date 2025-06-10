from django.db import models
from partido.models import Partido
from usuario.models import Usuario

class PartidoVotacionUsuario(models.Model):
    partido = models.ForeignKey(Partido, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    equipo_local_goles = models.IntegerField(default=0)
    equipo_visitante_goles = models.IntegerField(default=0)

    def __str__(self):
        return f'Votación de {self.usuario} en {self.partido}. Equipo local {self.equipo_local_goles}, equipo visitante {self.equipo_visitante_goles} '

