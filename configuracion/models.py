from django.db import models



class Configuracion(models.Model):
    # torneo = models.OneToOneField(Torneo, on_delete=models.CASCADE)
    monto_inicial_por_jugador = models.DecimalField(max_digits=10, decimal_places=2)
    porciento_acciones_maximo_por_jugador = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"Configuración de {self.monto_inicial_por_jugador}"
