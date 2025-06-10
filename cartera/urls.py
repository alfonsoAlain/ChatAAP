from django.urls import path, include
from rest_framework.routers import DefaultRouter

from cartera.views import CarteraViewSet

router = DefaultRouter()
router.register(r'', CarteraViewSet)
# router.register(r'carteras', CarteraViewSet, basename='cartera')  # Define un prefijo claro
urlpatterns = [
    path('', include(router.urls)),
]
