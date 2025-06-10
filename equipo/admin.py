from django.contrib import admin
from .models import Equipo, HistorialValorAccion


# Registra el modelo Equipo con el admin  
# admin.site.register(Equipo)


@admin.register(HistorialValorAccion)
class HistorialValorAccionAdmin(admin.ModelAdmin):
    list_display = ('equipo', 'fecha', 'valor_accion')  # Campos que deseas mostrar en la lista
    search_fields = ('equipo__nombre',)  # Permitir búsqueda por el nombre del equipo
    list_filter = ('equipo', 'fecha')  # Filtros por equipo y fecha

@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cantidad_acciones', 'valor_inicial_accion_display')

    def valor_inicial_accion_display(self, obj):
        return obj.valor_inicial_accion

    valor_inicial_accion_display.short_description = "Valor de Acciones"

