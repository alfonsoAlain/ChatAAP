from django.contrib import admin
from .models import RankingUsuario

@admin.register(RankingUsuario)
class RankingUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'total_valor_acciones','fecha_calculo')
    search_fields = ('usuario__username', 'usuario__nombre', 'usuario__apellido', 'fecha_calculo')
    list_filter = ('usuario__nombre', 'usuario__apellido','fecha_calculo')
    ordering = ('-total_valor_acciones',)
