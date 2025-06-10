from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HistoricoEquipoViewSet

router = DefaultRouter()
# router.register(r'', HistoricoEquipoViewSet)
router.register(r'(?P<equipo_id>\d+)/historicos', HistoricoEquipoViewSet, basename='historico_equipo')

urlpatterns = [
    path('', include(router.urls)),
]