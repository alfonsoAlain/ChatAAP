from django.db import models

from usuario.models import Usuario

class Cartera(models.Model):  
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) 
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)#Cambiando la relacion

    def __str__(self):  
        return f'Cartera de {self.usuario.nombre}'
