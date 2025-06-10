from django.http import Http404
from django.urls import path, include
from dj_rest_auth.views import LogoutView, PasswordResetView, PasswordResetConfirmView
from django.views.generic import TemplateView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from rest_framework.routers import DefaultRouter  
from .views import UsuarioViewSet, CustomLoginView, RegisterView, LogoutAllView, CustomPasswordChangeView, \
    CustomConfirmEmailView
from allauth.account.views import ConfirmEmailView
from django.conf import settings
from .views import CustomPasswordResetView
from django.contrib.auth.views import PasswordResetDoneView  


router = DefaultRouter()
router.register(r'', UsuarioViewSet)


urlpatterns = [
    path('', include(router.urls)),  # Rutas para el ViewSet  
    path('auth/login/', CustomLoginView.as_view(), name='rest_login'),   
    path('auth/logout/', LogoutView.as_view(), name='rest_logout'),  
    path('auth/register/', RegisterView.as_view(), name='rest_register'),  
    # path('jwt/create/', TokenObtainPairView.as_view(), name='token_create'),
    # path('jwt/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/login/verify/', TokenVerifyView.as_view(), name="token_verify"),
    path('logout/', LogoutAllView.as_view(), name='token_logout'),
    path('accounts/', include('allauth.urls')),

    path('password/change/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('password/reset/', PasswordResetView.as_view(), name='password_reset'),
    #path('password/reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password/reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),  # Agrega esta línea  
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password/reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # Estas dos urls deben ser sobreescritas con TemplateView para que no se renderice contenido.
    path('account-confirm-email/<str:key>/', CustomConfirmEmailView.as_view(), name='account_confirm_email'),
    path('account-email-verification-sent/', TemplateView.as_view(), name='account_email_verification_sent'),
] 
