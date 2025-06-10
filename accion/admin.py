from django.contrib import admin

from .models import Accion

# admin.site.register(Accion)

@admin.register(Accion)
class AccionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'equipo', 'cantidad')

