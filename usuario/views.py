from django.contrib.auth import authenticate
from django.http import JsonResponse, Http404

from django.forms import ValidationError
from rest_framework.response import Response
from rest_framework import viewsets, status, generics

from accion.models import Accion
from .models import Usuario
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from .serializers import UsuarioSerializer, RegisterSerializer, UsuarioRankingSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
# Autenticacion
import logging
# Para cambio de Contraseña
from django.conf import settings
from django.core.mail import EmailMessage, get_connection
from dj_rest_auth.views import PasswordChangeView
from django.shortcuts import redirect
from allauth.account.views import ConfirmEmailView


class UsuarioViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]  # Permitir el acceso a cualquier usuario   
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    def create(self, request, *args, **kwargs):
        print(Usuario.objects.values_list('username', flat=True))
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error en el registro: {str(e)}")  # Log para diagnósticos 
            print(f"Error: {str(e)}")
            print(f"Serializer errors: {serializer.errors}")
            return Response({"error": "Error al crear el usuario"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request, *args, **kwargs):
        print('Users:', self.queryset)
        return super().list(request, *args, **kwargs)


logger = logging.getLogger(__name__)


class CustomLoginView(APIView):
    def post(self, request, *args, **kwargs):
        logger.info("User is trying to log in")
        email = request.data.get('email')
        password = request.data.get('password')

        logger.info("User is trying to log in with email: {}".format(email))

        try:
            user = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            return JsonResponse({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

        user = authenticate(username=user.username, password=password)

        if user is not None:
            logger.info("User {} logged in successfully".format(email))
            access = AccessToken.for_user(user)
            refresh = RefreshToken.for_user(user)

            return JsonResponse({
                'access': str(access),
                'refresh': str(refresh),
                'user': {
                    'pk': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_superuser': user.is_superuser,  # Agregar el estado de superusuario
                }
            }, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LogoutAllView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        tokens = OutstandingToken.objects.filter(user_id=request.user.id)
        for token in tokens:
            t, _ = BlacklistedToken.objects.get_or_create(token=token)

        return Response(status=status.HTTP_205_RESET_CONTENT)


class UsuarioRankingView(generics.ListAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioRankingSerializer

    def get_queryset(self):
        # Obtiene todos los usuarios y los ordena por total_valor_acciones en orden descendente.
        usuarios = super().get_queryset()
        respuesta = sorted(usuarios, key=self.calcular_valor_acciones, reverse=True)
        return respuesta

    def calcular_valor_acciones(self, usuario):
        # Realiza una consulta para obtener las acciones del usuario
        acciones = Accion.objects.filter(usuario=usuario)
        # Calcula el valor total de las acciones
        total = sum(a.cantidad * a.equipo.valor_inicial_accion for a in acciones)
        return total + usuario.cartera.saldo


class CustomConfirmEmailView(ConfirmEmailView):
    def get(self, *args, **kwargs):
        try:
            self.object = self.get_object()
            if settings.ACCOUNT_CONFIRM_EMAIL_ON_GET:
                return self.post(*args, **kwargs)
        except Http404:
            self.object = None
            return redirect(settings.EMAIL_VERIFICATION_URL_NOT_VALID_URL)


class CustomPasswordChangeView(PasswordChangeView):

    def send_email_on_change(self, user):
        with get_connection(
                host=settings.EMAIL_HOST,
                port=settings.EMAIL_PORT,
                username=settings.EMAIL_HOST_USER,
                password=settings.EMAIL_HOST_PASSWORD,
                use_tls=settings.EMAIL_USE_TLS
        ) as connection:
            subject = f"Your password has been changed on {settings.FRONT_DOMAIN_NAME}"
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user.email]
            message = f"Hello, {user.username}.\nYou are receiving this email because your " \
                      f"password has been changed at {settings.FRONT_DOMAIN_NAME}. If so, please " \
                      f"ignore this message.\nOtherwise, go to {settings.LOGIN_URL} and check " \
                      f"forgot password to reset your password." \
                      f"\nRegards from the {settings.FRONT_DOMAIN_NAME} team."

            EmailMessage(subject, message, email_from, recipient_list, connection=connection).send()

    def post(self, request, *args, **kwargs):
        response = super(CustomPasswordChangeView, self).post(request, args, kwargs)
        self.send_email_on_change(request.user)
        return response

from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView

class CustomPasswordResetView(PasswordResetView):

    def send_email_on_request(self, user):
        # Crea una conexión con el servidor SMTP
        with get_connection(
            host=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            username=settings.EMAIL_HOST_USER,
            password=settings.EMAIL_HOST_PASSWORD,
            use_tls=settings.EMAIL_USE_TLS
        ) as connection:
            subject = f"Password Reset Request for {settings.FRONT_DOMAIN_NAME}"
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user.email]
            message = f"Holaaa {user.username},\n\n" \
                      f"Tu estas Probando You are receiving this email because we received a password reset request for your account at {settings.FRONT_DOMAIN_NAME}." \
                      f"\nIf you did not request a password reset, no further action is required.\n" \
                      f"If you did request this, please follow the instructions in the email to reset your password.\n" \
                      f"\nRegards from the {settings.FRONT_DOMAIN_NAME} team."

            # Envía el email usando la conexión
            EmailMessage(subject, message, email_from, recipient_list, connection=connection).send()

    def form_valid(self, form):
        # Llama al método original para procesar el formulario
        response = super(CustomPasswordResetView, self).form_valid(form)

        # Envía un correo electrónico de notificación al usuario
        users = self.get_users(form.cleaned_data["email"])  
        for user in users:  
            self.send_email_on_request(user)

        return redirect(reverse('usuarios:password_reset_done'))  # Redirige a la vista 'password_reset_done'  
