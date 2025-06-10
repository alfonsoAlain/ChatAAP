from django.contrib import admin

from .models import Partido

# admin.site.register(Partido)

@admin.register(Partido)
class PartidoAdmin(admin.ModelAdmin):
    list_display = ('equipo_local', 'equipo_visitante', 'torneo', 'estado','fecha')

