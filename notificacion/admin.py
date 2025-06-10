from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db import models

from notificacion.models import Notificacion, NotificacionUsuario


class NotificacionUsuarioInline(admin.TabularInline):
    model = NotificacionUsuario
    extra = 3
    # autocomplete_fields = ['usuarios']



@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    inlines = [NotificacionUsuarioInline, ]
    list_display = ('titulo', 'mensaje', 'tipo')
    # search_fields = ('titulo', 'mensaje')
    filter_horizontal = ('usuarios',)

