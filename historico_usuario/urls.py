from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HistoricoUsuarioViewSet

router = DefaultRouter()
# router.register(r'', HistoricoUsuarioViewSet)
router.register(r'', HistoricoUsuarioViewSet, basename='historico_usuario')

urlpatterns = [
    path('', include(router.urls)),
]