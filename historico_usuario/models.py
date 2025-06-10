from django.db import models

from historico_equipo.models import HistoricoEquipo
from usuario.models import Usuario


class HistoricoUsuario(models.Model):
    OPERACION_CHOICES = [
        ('compra', 'Compra'),
        ('venta', 'Venta'),
    ]

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    operacion = models.CharField(max_length=10, choices=OPERACION_CHOICES)
    historico_equipo = models.ForeignKey(HistoricoEquipo, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Histórico de Usuario"
        verbose_name_plural = "Históricos de Usuarios"
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.usuario.nombre} - {self.operacion} - {self.historico_equipo.equipo.nombre} - {self.fecha}"
