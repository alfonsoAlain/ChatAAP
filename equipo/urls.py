from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EquipoViewSet, HistoricoAccionEquipoViewSet, FootballTeamsAPIView
from historico_equipo.views import HistoricoEquipoViewSet, DiferenciaPrecioAPIView

router = DefaultRouter()
router.register(r'', EquipoViewSet, basename='equipo')

urlpatterns = [
    path('', include(router.urls)),
    path('importar/football-teams/', FootballTeamsAPIView.as_view(), name='football-teams'),
    path('precio/variacion/', DiferenciaPrecioAPIView.as_view(), name='diferencia_precio'),
    path('<int:equipo_id>/historico/', HistoricoEquipoViewSet.as_view({'get': 'list'}), name='historico_equipo'),
    path('<int:equipo_id>/historico-accion/', HistoricoAccionEquipoViewSet.as_view({'get': 'list'}), name='historico_accion_equipo'),
]
