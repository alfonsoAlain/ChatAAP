from django.apps import AppConfig


class EquipoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'equipo'

    def ready(self):
        import equipo.signals  # importa las señales cuando se cargue la app