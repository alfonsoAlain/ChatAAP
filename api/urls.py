"""
URL configuration for api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/usuarios/', include('usuario.urls')),  # Prefijo para la app usuario
    # path('api/v1/equipos/', include('equipo.urls')),    # Prefijo para la app equipo
    # path('api/v1/torneos/', include('torneo.urls')),    # Prefijo para la app torneo
    # path('api/v1/carteras/', include('cartera.urls')),    # Prefijo para la app cartera
    # path('api/v1/partidos/', include('partido.urls')),    # Prefijo para la app partido
    # path('api/v1/', include('transaccion_pendiente.urls')),  # Prefijo para la app transaccion_pendiente
    # path('api/v1/acciones/', include('accion.urls')),    # Prefijo para la app accion
    # path('api/v1/notificaciones/', include('notificacion.urls')),    # Prefijo para la app notificacion
    # path('api/v1/', include('partido_votacion_usuario.urls')),    # Prefijo para la app partido_votacion_usuario
    # path('api/v1/historico-ranking-usuarios/', RankingUsuarioListView.as_view(), name='historico-ranking-usuarios'),
    # path('api/v1/ranking-usuarios/', UsuarioRankingView.as_view(), name='ranking-usuarios'),
    # # path('api/v1/ranking-usuarios/calculate/', UsuarioRankingCreateView.as_view(), name='ranking-usuarios-calculate'),
    # path('api/v1/historico-usuarios/', include('historico_usuario.urls')),
    # path('api/v1/ranking-usuario-fecha/', RankingUsuarioFechaView.as_view(), name='ranking-usuario-fecha'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
