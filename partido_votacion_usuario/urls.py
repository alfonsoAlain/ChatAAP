from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PartidoVotacionUsuarioViewSet

router = DefaultRouter()
router.register(r'partido-votacion-usuarios', PartidoVotacionUsuarioViewSet)
# router.register(r'partido-votacion-usuarios', )

urlpatterns = [
    path('', include(router.urls))
]
