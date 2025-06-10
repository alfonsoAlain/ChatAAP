from django.db import models


class Equipo(models.Model):
    nombre = models.CharField(max_length=255)
    escudo = models.ImageField(upload_to='escudos/', default='ur.png')
    cantidad_acciones = models.IntegerField()
    valor_inicial_accion = models.DecimalField(max_digits=10, decimal_places=2)
    limite_diario_variacion_precio = models.DecimalField(max_digits=5, decimal_places=2)
    limite_acciones_jugador = models.IntegerField()
    liga_base = models.CharField(max_length=5, null=True, blank=True)
    id_externo = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.nombre

    def ajuste(self, equipo_ganador, equipo_perdedor, resultado, torneo):
        print(f"Ajustando acciones para: {equipo_ganador.nombre} y {equipo_perdedor.nombre}")

        if torneo.tipo == 'A':
            multiplicador = 1
        elif torneo.tipo == 'L':
            multiplicador = 2
        elif torneo.tipo == 'I':
            multiplicador = 3
        else:
            print("Tipo de torneo no válido")
            return  # Tipo de torneo no válido

        # Ajustar el valor de las acciones
        incremento_ganador = resultado * multiplicador
        decremento_perdedor = -1 * multiplicador
        print(f"Incremento ganando: {incremento_ganador}, Decremento perdiendo: {decremento_perdedor}")

        # Aplicar el ajuste a los equipos
        nuevo_valor_ganador = equipo_ganador.valor_inicial_accion + incremento_ganador
        nuevo_valor_perdedor = equipo_perdedor.valor_inicial_accion + decremento_perdedor

        # Aplicar el ajuste a los equipos
        equipo_ganador.valor_inicial_accion = nuevo_valor_ganador
        equipo_perdedor.valor_inicial_accion = nuevo_valor_perdedor

        # Guardar los cambios en la base de datos
        # Actualizar el precio en las transacciones pendientes
        from transaccion_pendiente.models import TransaccionPendiente
        TransaccionPendiente.objects.filter(equipo=equipo_ganador).update(precio=nuevo_valor_ganador)
        TransaccionPendiente.objects.filter(equipo=equipo_perdedor).update(precio=nuevo_valor_perdedor)

        equipo_ganador.save()
        equipo_perdedor.save()
        print(
            f"Valores ajustados: {equipo_ganador.nombre}: {equipo_ganador.valor_inicial_accion}, {equipo_perdedor.nombre}: {equipo_perdedor.valor_inicial_accion}")


class HistorialValorAccion(models.Model):
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='historial_valores')
    fecha = models.DateTimeField(auto_now_add=True)
    valor_accion = models.DecimalField(max_digits=10, decimal_places=2)

