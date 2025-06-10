from django.db import models

from usuario.models import Usuario


class Notificacion(models.Model):
    TIPO_NOTIFICACION_OPCIONES = [
        ('CB', 'Banca contraoferta'),
        ('NB', 'Banca notifica'),
    ]
    titulo = models.CharField(max_length=100, null=True)
    mensaje = models.CharField(max_length=255)
    tipo = models.CharField(max_length=2, choices=TIPO_NOTIFICACION_OPCIONES, default='NB')
    fechaInicio = models.DateTimeField(null=True, blank=True)
    fechaFin = models.DateTimeField(null=True, blank=True)
    usuarios = models.ManyToManyField(Usuario, through='NotificacionUsuario', related_name='notificaciones')

    def __str__(self):
        return self.mensaje


class NotificacionUsuario(models.Model):
    usuario = models.ForeignKey(Usuario, related_name='read_notificacions', on_delete=models.CASCADE)
    notificacion = models.ForeignKey(Notificacion, related_name='leido_por', on_delete=models.CASCADE)
    fecha_leido = models.DateTimeField(null=True, blank=True)

    # class Meta:
    #     unique_together = ('usuario', 'notificacion')

    def __str__(self):
        return f'NotificationRead: {self.notificacion.titulo} read by {self.usuario} at {self.fecha_leido}'


