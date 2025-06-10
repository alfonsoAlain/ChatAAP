from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer

from accion.models import Accion
from equipo.models import Equipo
from .models import Usuario
from cartera.models import Cartera
# Autenticacion
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = [
            'nombre',
            'apellido',
            'documento',
            'celular',
            'telefono',
            'email',
            'password',
            'accept_terms_conditions',
            'equipo_preferido',
        ]
        extra_kwargs = {
            'password': {'write_only': True}  # Asegúrate de que la contraseña no se devuelva en las respuestas  
        }

    def create(self, validated_data):
        # Comprobar si el username o email ya existe  
        if Usuario.objects.filter(username=validated_data['username']).exists():
            raise ValidationError("El nombre de usuario ya está en uso.")

        if Usuario.objects.filter(email=validated_data['email']).exists():
            raise ValidationError("El correo electrónico ya está en uso.")

        usuario = Usuario(**validated_data)
        usuario.set_password(validated_data['password'])
        usuario.save()
        return usuario

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == 'password':
                instance.set_password(value)  # Asegúrate de encriptar la contraseña en la actualización  
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        user = authenticate(username=username, password=password)

        if user is None:
            raise serializers.ValidationError('Invalid username or password.')

        attrs['user'] = user
        return attrs


class CustomRegisterSerializer(RegisterSerializer):
    username = serializers.CharField(required=True)

    def save(self, request):
        user = super().save(request)
        user.username = self.cleaned_data.get('username')
        user.save()
        return user


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    equipo_preferido = serializers.PrimaryKeyRelatedField(
        queryset=Equipo.objects.all(),  # Cambia esto según cómo obtengas tu lista de equipos
        allow_null=True,  # Permitir que este campo sea opcional
        required=False  # También opcional en la validación
    )

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password', 'nombre', 'apellido', 'documento', 'celular', 'telefono', 'edad',
                  'accept_terms_conditions', 'equipo_preferido']
        # extra_kwargs = {
        #     'password1': {'write_only': True},
        #     'password2': {'write_only': True},
        # }

    def create(self, validated_data):
        user = Usuario(
            username=validated_data['username'],
            email=validated_data['email'],
            nombre=validated_data['nombre'],
            apellido=validated_data['apellido'],
            documento=validated_data['documento'],
            celular=validated_data['celular'],
            telefono=validated_data.get('telefono', ''),
            accept_terms_conditions=validated_data['accept_terms_conditions'],
            equipo_preferido=validated_data.get('equipo_preferido'),  # Campo opcional
        )
        user.set_password(validated_data['password'])
        user.save()

        Cartera.objects.create(usuario=user, saldo=1000.00)

        return user


class UsuarioRankingSerializer(serializers.ModelSerializer):
    total_valor_acciones = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = ['id', 'username', 'nombre', 'apellido', 'total_valor_acciones']

    def get_total_valor_acciones(self, usuario):
        acciones = Accion.objects.filter(usuario=usuario)
        total = sum(accion.cantidad * accion.equipo.valor_inicial_accion for accion in acciones)
        return total + usuario.cartera.saldo
