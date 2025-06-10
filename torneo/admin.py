from django.contrib import admin

from .models import Torneo

#admin.site.register(Torneo)

@admin.register(Torneo)
class TorneoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fechaInicio', 'fechaFin', 'tipo')
