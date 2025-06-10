from django.urls import path, include
from rest_framework.routers import DefaultRouter

from notificacion.views import NotificacionViewSet, NotificationUsuarioViewSet

router = DefaultRouter()
router.register(r'', NotificacionViewSet)
router.register(r'notificaciones-usuarios', NotificationUsuarioViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
