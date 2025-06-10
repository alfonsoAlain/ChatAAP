from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransaccionPendienteViewSet, MisTransaccionPendienteViewSet

router = DefaultRouter()
router.register(r'transacciones-pendientes', TransaccionPendienteViewSet, basename='transacciones-pendientes'),
router.register(r'mis-transacciones-pendientes', MisTransaccionPendienteViewSet, basename='mis-transacciones-pendientes'),

urlpatterns = [
    path('', include(router.urls)),
    path('<int:transaccion_id>/borrar-equipo/<int:equipo_id>/',
         TransaccionPendienteViewSet.as_view({'delete': 'destroy_equipo_from_transaccion'}),
         name='borrar-equipo-de-transaccion'),
]
