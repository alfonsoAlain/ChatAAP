from django.db import models

from equipo.models import Equipo


class HistoricoEquipo(models.Model):
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.IntegerField()

    class Meta:
        verbose_name = "Histórico de Equipo"
        verbose_name_plural = "Históricos de Equipos"
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.equipo.nombre} - {self.fecha} - ${self.precio} - Cantidad: {self.cantidad}"
