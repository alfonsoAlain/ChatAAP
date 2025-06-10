from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PartidoViewSet, FootballMatchesAPIView, FootballUpdateMatchesStatusAPIView, MatchDetailView

router = DefaultRouter()
router.register(r'', PartidoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('importar/football-matches/', FootballMatchesAPIView.as_view(), name='importar-football-matches'),
    path('actualizar/football-matches/', FootballUpdateMatchesStatusAPIView.as_view(), name='actualizar-football'
                                                                                            '-matches'),
    path('obtener/football-matches/', MatchDetailView.as_view(), name='obtener-football-matches'),
]
