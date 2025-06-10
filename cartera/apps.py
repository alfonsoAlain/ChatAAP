# cartera/apps.py
from django.apps import AppConfig

class CarteraConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cartera'

    def ready(self):
        import cartera.signals