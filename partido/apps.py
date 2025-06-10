from django.apps import AppConfig


class PartidoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'partido'

    def ready(self):
        import partido.signals  # Asegúrate de importar el archivo signals aquí
