from django.contrib import admin

from .models import Usuario

# admin.site.register(Usuario)

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'nombre', 'apellido', 'email', 'equipo_preferido')
