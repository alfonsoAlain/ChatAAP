import base64

from django.db import transaction
from rest_framework import serializers, status
from rest_framework.response import Response

from equipo.models import Equipo
from transaccion_pendiente.models import TransaccionPendiente
from accion.models import Accion
from usuario.models import Usuario



class TransaccionPendienteSerializer(serializers.ModelSerializer):
    equipo_id = serializers.PrimaryKeyRelatedField(source='equipo.id', queryset=Equipo.objects.all())
    equipo_nombre = serializers.SerializerMethodField()
    escudo = serializers.SerializerMethodField()

    usuario_id = serializers.PrimaryKeyRelatedField(source='usuario.id', read_only=True)
    usuario_nombre = serializers.SerializerMethodField()

    class Meta:
        model = TransaccionPendiente
        fields = ['id', 'usuario_id', 'usuario_nombre', 'equipo_id', 'equipo_nombre', 'cantidad', 'precio', 'fecha', 'escudo']

    def create(self, validated_data):
        usuario = self.context['request'].user
        validated_data['usuario'] = usuario  # Añado el usuario a los datos validados

        # Crea la transacción pendiente
        transaccion = TransaccionPendiente.objects.create(**validated_data)

        # Supongamos que validated_data incluye un campo que indica la cantidad de acciones a descontar
        cantidad_acciones = validated_data.get('cantidad')
        equipo = validated_data.get('equipo')
        # precio = validated_data.get('precio')
        # Descontar acciones del modelo Acciones
        try:
            acciones = Accion.objects.get(usuario=usuario, equipo=equipo)  # Busca las acciones del usuario
            if acciones.cantidad > cantidad_acciones:  # Verifica que haya suficientes acciones
                acciones.cantidad -= cantidad_acciones  # Descuenta la cantidad
                acciones.save()  # Guarda los cambios
            else:
                acciones.delete()
                # raise serializers.ValidationError('No hay suficientes acciones para completar la transacción.')
        except Accion.DoesNotExist:
            raise serializers.ValidationError('El usuario no tiene un registro de acciones.')
            # accion = Accion.objects.create(**validated_data)

        return transaccion

    def update(self, instance, validated_data):
        usuario = self.context['request'].user
        nuevo_equipo = validated_data.get('equipo', instance.equipo)
        nueva_cantidad = validated_data.get('cantidad', instance.cantidad)
        cantidad_original = instance.cantidad

        diferencia = nueva_cantidad - cantidad_original

        # Si no hay cambio de cantidad, simplemente actualiza otros campos
        if diferencia == 0:
            instance.precio = validated_data.get('precio', instance.precio)
            instance.save()
            return instance

        try:
            accion = Accion.objects.get(usuario=usuario, equipo=nuevo_equipo)
        except Accion.DoesNotExist:
            accion = None

        if diferencia > 0:
            # Quiere aumentar la cantidad de la transacción → descontar más acciones
            if accion:
                if accion.cantidad >= diferencia:
                    accion.cantidad -= diferencia
                else:
                    raise serializers.ValidationError("No hay suficientes acciones para aumentar la transacción.")
            else:
                raise serializers.ValidationError("No tienes acciones suficientes para realizar esta transacción.")
        elif diferencia < 0:
            # Disminuyó la cantidad → devolver acciones
            if accion:
                accion.cantidad += abs(diferencia)
            else:
                # Crear la acción si no existe
                accion = Accion(usuario=usuario, equipo=nuevo_equipo, cantidad=abs(diferencia))

        # Guardar o eliminar la acción si corresponde
        if accion.cantidad == 0:
            accion.delete()
        else:
            accion.save()

        # Actualizar la instancia
        instance.cantidad = nueva_cantidad
        instance.precio = validated_data.get('precio', instance.precio)
        instance.save()

        return instance

    def perform_destroy(self, instance):
        """
        Método corregido para manejar la eliminación de transacciones
        """
        usuario = instance.usuario
        equipo = instance.equipo
        cantidad = instance.cantidad

        with transaction.atomic():
            # Buscar o crear la acción
            accion, created = Accion.objects.get_or_create(
                usuario=usuario,
                equipo=equipo,
                defaults={'cantidad': cantidad}
            )

            # Si la acción ya existía, sumar la cantidad
            if not created:
                accion.cantidad += cantidad
                accion.save()

            # Eliminar la transacción
            instance.delete()

    def get_equipo_nombre(self, obj):
        return obj.equipo.nombre if obj.equipo else None

    def get_escudo(self, obj):
        if obj.equipo and obj.equipo.escudo:
            escudo_file = obj.equipo.escudo
            # Leer el archivo de la imagen en binario
            with escudo_file.open('rb') as image_file:
                # Codificar a base64
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return encoded_string
        return None

    def get_usuario_nombre(self, obj):
        return obj.usuario.nombre if obj.usuario else None
