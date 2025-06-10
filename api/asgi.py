"""
ASGI config for api project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""
import os
import django
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Establecer la variable de entorno para la configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')

# Inicializar Django
django.setup()

# Importar módulos que dependen de Django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from cartera.middleware import JWTAuthMiddleware
# from partido.routing import websocket_urlpatterns  # Asegúrate de usar el nombre correcto de la app

# Mostrar el valor de la variable de entorno (puedes eliminar esto en producción)
# print(f"DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")

# Definir la aplicación ASGI
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')

import partido.routing
import equipo.routing
import cartera.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthMiddleware(
        URLRouter(
            partido.routing.websocket_urlpatterns +
            equipo.routing.websocket_urlpatterns +
            cartera.routing.websocket_urlpatterns

        )
    ),
})