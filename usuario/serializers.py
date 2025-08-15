from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer

from .models import Usuario
# Autenticacion
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError


class UsuarioSerializer(serializers.ModelSerializer):
    nombre = serializers.SerializerMethodField()
    apellido = serializers.SerializerMethodField()
    class Meta:
        model = Usuario
        fields = [
            'id',
            'nombre',
            'apellido',
            'documento',
            'celular',
            'telefono',
            'email',
            'password',
            'accept_terms_conditions',
        ]
        extra_kwargs = {
            'password': {'write_only': True}  # Asegúrate de que la contraseña no se devuelva en las respuestas  
        }

    def get_nombre(self, obj):
        if not obj.nombre or obj.nombre.strip().lower() == "no definido":
            return obj.username
        return obj.nombre

    def get_apellido(self, obj):
        if not obj.apellido or obj.apellido.strip().lower() == "no definido":
            return obj.username
        return obj.apellido

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
    nombre = serializers.CharField(required=False, allow_blank=True)
    apellido = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Usuario
        fields = [
            'username', 'email', 'password', 'nombre', 'apellido', 'documento',
            'celular', 'telefono', 'accept_terms_conditions', 'public_key'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = Usuario(
            username=validated_data['username'],
            email=validated_data['email'],
            nombre=validated_data.get('nombre', ''),
            apellido=validated_data.get('apellido', ''),
            documento=validated_data['documento'],
            celular=validated_data['celular'],
            telefono=validated_data.get('telefono', ''),
            accept_terms_conditions=validated_data['accept_terms_conditions'],
            public_key=validated_data.get('public_key', ''),
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def to_representation(self, instance):
        """Al devolver datos, calculamos nombre/apellido si están vacíos."""
        rep = super().to_representation(instance)
        if not rep.get('nombre'):
            rep['nombre'] = instance.username.split()[0] if instance.username else ''
        if not rep.get('apellido'):
            rep['apellido'] = instance.username.split()[1] if instance.username and len(instance.username.split()) > 1 else ''
        return rep

class UsuarioRankingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Usuario
        fields = ['id', 'username', 'nombre', 'apellido']


class UsuarioChatSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = ['id', 'username', 'nombre', 'apellido', 'profile_image', 'public_key']

    def get_profile_image(self, obj):
        if obj.profile_image:
            return obj.profile_image.url
        return None

    def get_nombre(self, obj):
        return obj.nombre if obj.nombre else obj.username

    def get_apellido(self, obj):
        return obj.apellido if obj.apellido else obj.username