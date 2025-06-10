# from django.db import models
#
# from equipo.models import Equipo
#
#
# class TransaccionPendiente(models.Model):
#     equipos = models.ManyToManyField(Equipo, through='EquipoTransaccion')
#
#     def __str__(self):
#         return f"Transacción Pendiente ID: {self.id}"
#
# class EquipoTransaccion(models.Model):
#     transaccion = models.ForeignKey(TransaccionPendiente, on_delete=models.CASCADE)
#     equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)
#     cantidad = models.IntegerField()
#     precio = models.DecimalField(max_digits=10, decimal_places=2)
#
#     def __str__(self):
#         return f"{self.equipo} - Cantidad: {self.cantidad} - Precio: {self.precio}"

# from django.db import models
#
#
# class Equipo(models.Model):
#     nombre = models.CharField(max_length=100)
#
#     def __str__(self):
#         return self.nombre
#
#
# class TransaccionPendiente(models.Model):
#     fecha = models.DateTimeField(auto_now_add=True, null=True)
#     equipos = models.ManyToManyField(Equipo, through='EquipoTransaccion')
#
#     def __str__(self):
#         return f'Transacción {self.id}'
#
#
# class EquipoTransaccion(models.Model):
#     transaccion = models.ForeignKey(TransaccionPendiente, related_name='equipostransaccion', on_delete=models.CASCADE)
#     equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)
#     cantidad = models.PositiveIntegerField(default=1)
#     precio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
#
#     def __str__(self):
#         return f'{self.cantidad} x {self.equipo} en {self.transaccion}'

from django.db import models

from equipo.models import Equipo
from usuario.models import Usuario


class TransaccionPendiente(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True)
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, null=True)
    cantidad = models.PositiveIntegerField(default=1)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Transacción de {self.usuario} para {self.equipo}'
