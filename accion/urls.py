from django.urls import path, include
from rest_framework.routers import DefaultRouter

from accion.views import AccionViewSet

router = DefaultRouter()
router.register(r'', AccionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]