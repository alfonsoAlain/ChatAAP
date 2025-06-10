import base64

from django.db import transaction

from cartera.models import Cartera
from configuracion.models import Configuracion
from equipo.models import Equipo
from usuario.models import Usuario
from historico_equipo.models import HistoricoEquipo
from historico_usuario.models import HistoricoUsuario
from .models import Accion
from transaccion_pendiente.models import TransaccionPendiente
from rest_framework import serializers


class AccionSerializer(serializers.ModelSerializer):
    escudo = serializers.SerializerMethodField()
    nombre_equipo = serializers.SerializerMethodField()
    valor_actual_mercado = serializers.SerializerMethodField()
    id_transaccion = serializers.IntegerField(write_only=True)
    promedio_compra = serializers.SerializerMethodField()
    class Meta:
        model = Accion
        fields = ['id', 'cantidad', 'equipo', 'usuario', 'escudo', 'nombre_equipo', 'id_transaccion', 'valor_actual_mercado', 'promedio_compra']


    def get_escudo(self, obj):
        # Obtener el equipo relacionado
        equipo = obj.equipo  # Asumiendo que 'equipo' es una relación en el modelo Accion
        if equipo and equipo.escudo:
            with open(equipo.escudo.path, "rb") as image_file:
                # Convertir la imagen a base64
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                return encoded_string
        return None

    def get_nombre_equipo(self, obj):
        # Retornar el nombre del equipo
        return obj.equipo.nombre if obj.equipo else None

    def get_valor_actual_mercado(self, obj):
        # Retornar el valor_inicial_accion del equipo
        return obj.equipo.valor_inicial_accion if obj.equipo else None

    def get_promedio_compra(self, obj):
        # Obtener el promedio ponderado de compra
        históricos = HistoricoUsuario.objects.filter(usuario=obj.usuario, historico_equipo__equipo=obj.equipo,
                                                     operacion='compra')
        total_comprado = 0
        total_invertido = 0
        for histórico in históricos:
            total_comprado += histórico.historico_equipo.cantidad
            total_invertido += histórico.historico_equipo.cantidad * histórico.historico_equipo.precio
        if total_comprado > 0:
            return total_invertido / total_comprado
        else:
            return 0

    def create(self, validated_data):
        usuario_autenticado = validated_data.pop('usuario_autenticado')
        id_transaccion = validated_data.pop('id_transaccion')
        id_usuario = validated_data['usuario']
        id_equipo = validated_data['equipo']
        cantidad = validated_data['cantidad']

        usuario_autenticado = Usuario.objects.get(username=usuario_autenticado)

        try:
            with transaction.atomic():  # Inicia la transacción atómica

                carteraComprador = Cartera.objects.get(usuario=usuario_autenticado)
                carteraVendedor = Cartera.objects.get(usuario=id_usuario)

                # Obtener el equipo correspondiente
                equipo = Equipo.objects.get(nombre=id_equipo)

                if not equipo:
                    raise serializers.ValidationError("El equipo no existe.")

                limite_acciones = equipo.limite_acciones_jugador

                # Verifico si se estableció el límite en el equipo
                if limite_acciones:

                    cantidad_permitida = (limite_acciones / 100) * equipo.cantidad_acciones

                    if cantidad > cantidad_permitida:
                        raise serializers.ValidationError("La cantidad excede las acciones permitidas del equipo.")

                else:  # Verifico si se estableció el límite en configuración

                    configuracion = Configuracion.objects.first()
                    limite_acciones = configuracion.porciento_acciones_maximo_por_jugador
                    porcentaje_permitido = (limite_acciones / 100) * equipo.cantidad_acciones
                    if cantidad > porcentaje_permitido:
                        raise serializers.ValidationError("La cantidad excede el acciones permitidas.")

                # Verifico si ya existe una acción para este usuario y equipo
                accion_existente = Accion.objects.filter(usuario=usuario_autenticado, equipo=id_equipo).first()

                if accion_existente:
                    # Obtengo el valor permitido
                    valor_permitido = (limite_acciones / 100) * equipo.cantidad_acciones

                    # Verifico si la cantidad pedida es menor a la permitida
                    if cantidad > valor_permitido:
                        raise serializers.ValidationError("La cantidad excede el acciones permitidas.")

                    # Decremento la cantidad de acciones del equipo
                    equipo.cantidad_acciones -= cantidad
                    equipo.save()

                    # Cargar la transacción pendiente
                    transaccion_pendiente = TransaccionPendiente.objects.filter(usuario=id_usuario, equipo=equipo.id,
                                                                                id=id_transaccion).first()
                    transaccion_precio = transaccion_pendiente.precio

                    if transaccion_pendiente is None:
                        raise serializers.ValidationError("Transacción pendiente no encontrada.")

                    if transaccion_pendiente.cantidad < cantidad:
                        raise serializers.ValidationError("La cantidad a decrementar excede la cantidad pendiente.")

                    precioCompra = transaccion_pendiente.precio * cantidad


                    if carteraComprador.saldo < precioCompra:
                        raise serializers.ValidationError("Usted no tiene saldo suficiente para la compra.")

                    # Descontar saldo
                    carteraComprador.saldo -= precioCompra
                    carteraComprador.save()
                    carteraVendedor.saldo += precioCompra
                    carteraVendedor.save()

                    usuario_vende = transaccion_pendiente.usuario

                    # Verificar si se está comprando la misma cantidad
                    if transaccion_pendiente.cantidad == cantidad:

                        transaccion_pendiente.delete()

                        # Sumo a la accion existente la cantidad pedida
                        accion_existente.cantidad += cantidad
                        accion_existente.save()

                    else:
                        # Decremento la cantidad en transaccion pendiente
                        transaccion_pendiente.cantidad -= cantidad
                        transaccion_pendiente.save()

                        # Sumo a la accion existente la cantidad pedida
                        accion_existente.cantidad += cantidad
                        accion_existente.save()

                    # Agregar a los historicos de usuario y de equipo
                    historico_equipo = HistoricoEquipo.objects.create(equipo=equipo, precio=transaccion_precio,
                                                                      cantidad=cantidad)

                    if historico_equipo is None:
                        raise serializers.ValidationError("Ocurrió un error al registrar en el histórico del equipo.")

                    historico_usuario_compra = HistoricoUsuario.objects.create(usuario=self.context['request'].user,
                                                                               historico_equipo=historico_equipo,
                                                                               operacion='compra')

                    if historico_usuario_compra is None:
                        raise serializers.ValidationError("Ocurrió un error al registrar en el histórico del usuario que compra.")

                    historico_usuario_vende = HistoricoUsuario.objects.create(usuario=usuario_vende,
                                                                              historico_equipo=historico_equipo,
                                                                              operacion='venta')
                    if historico_usuario_vende is None:
                        raise serializers.ValidationError(
                            "Ocurrió un error al registrar en el histórico del usuario que vende.")

                    return accion_existente  # Retornar la acción actualizada

                # Decremento en equipo
                equipo.cantidad_acciones -= cantidad
                equipo.save()

                # Cargar la transacción pendiente
                transaccion_pendiente = TransaccionPendiente.objects.filter(usuario=id_usuario, equipo=equipo.id,
                                                                            id=id_transaccion).first()

                if transaccion_pendiente is None:
                    raise serializers.ValidationError("Transacción pendiente no encontrada.")

                # Verifico en transaccion pendiente si la cantidad solicitada es mayor a la disponible en la transaccion
                if transaccion_pendiente.cantidad < cantidad:
                    raise serializers.ValidationError("La cantidad a decrementar excede la cantidad pendiente.")

                usuario_vende = transaccion_pendiente.usuario
                transaccion_precio = transaccion_pendiente.precio

                # Verifico en transaccion pendiente si la cantidad es igual a la solicitada y si es asi la elimino
                if transaccion_pendiente.cantidad == cantidad:

                    transaccion_pendiente.delete()

                else:# Si en transaccion pendiente la cantidad es mayor la resto

                    transaccion_pendiente.cantidad -= cantidad
                    transaccion_pendiente.save()

                precioCompra = transaccion_pendiente.precio * cantidad

                if carteraComprador.saldo < precioCompra:
                    raise serializers.ValidationError("Usted no tiene saldo suficiente para la compra.")

                # Decremento el precio de compra en la cartera del comprador
                carteraComprador.saldo -= precioCompra
                carteraComprador.save()

                # Decremento el precio de compra en la cartera del vendedor
                carteraVendedor.saldo += precioCompra
                carteraVendedor.save()

                # Quito del validated_data el usuario ya que el que necesito es el autenticado
                validated_data.pop('usuario', None)  # Elimina usuario si está presente

                # Agregar a los historicos de usuario y de equipo
                historico_equipo = HistoricoEquipo.objects.create(equipo=equipo, precio=transaccion_precio,
                                                                  cantidad=cantidad)

                if historico_equipo is None:
                    raise serializers.ValidationError("Ocurrió un error al registrar en el histórico del equipo.")

                historico_usuario_compra = HistoricoUsuario.objects.create(usuario=self.context['request'].user,
                                                                           historico_equipo=historico_equipo,
                                                                           operacion='compra')

                if historico_usuario_compra is None:
                    raise serializers.ValidationError(
                        "Ocurrió un error al registrar en el histórico del usuario que compra.")

                historico_usuario_vende = HistoricoUsuario.objects.create(usuario=usuario_vende,
                                                                          historico_equipo=historico_equipo,
                                                                          operacion='venta')
                if historico_usuario_vende is None:
                    raise serializers.ValidationError(
                        "Ocurrió un error al registrar en el histórico del usuario que vende.")

                return Accion.objects.create(usuario=self.context['request'].user, **validated_data)


        except Exception as e:
            raise serializers.ValidationError(e)


