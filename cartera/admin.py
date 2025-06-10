from django.contrib import admin

from .models import Cartera

# admin.site.register(Cartera)

@admin.register(Cartera)
class CarteraAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'usuario_email', 'saldo')

    def usuario_email(self, obj):
        return obj.usuario.email

    usuario_email.short_description = 'Email'