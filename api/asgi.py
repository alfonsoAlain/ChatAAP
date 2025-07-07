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

from message.middleware import JWTAuthMiddleware
import message.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthMiddleware(
        URLRouter(
            message.routing.websocket_urlpatterns

        )
    ),
})