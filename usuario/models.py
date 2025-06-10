from django.contrib.auth.models import AbstractUser, Group, Permission  
from django.db import models

from equipo.models import Equipo


class Usuario(AbstractUser):   
    nombre = models.CharField(max_length=30)  
    apellido = models.CharField(max_length=30)  
    documento = models.CharField(max_length=20, blank=True, null=True)  
    celular = models.CharField(max_length=15, blank=True, null=True)  
    telefono = models.CharField(max_length=15, blank=True, null=True)  
    email = models.EmailField(unique=True)  
    accept_terms_conditions = models.BooleanField(default=False)

    # Añade related_name para evitar conflictos  
    groups = models.ManyToManyField(  
        Group,  
        related_name='usuarios',
        blank=True  
    )  
    user_permissions = models.ManyToManyField(  
        Permission,  
        related_name='usuarios',
        blank=True  
    )   

    # Sobrescribir el atributo first_name  
    @property  
    def first_name(self):  
        return self.apellido  

    @first_name.setter  
    def first_name(self, value):  
        self.apellido = value 

    def __str__(self):  
        return self.username   
    
    class Meta:  
        verbose_name = 'Usuario'  
        verbose_name_plural = 'Usuarios'