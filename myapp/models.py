import uuid
from django.dispatch import receiver
from django.utils import timezone
from enum import Enum
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractBaseUser
from .managers import CustomUsuarioManager


class EstadoVehiculo(Enum):
    DISPONIBLE = 'Disponible'
    OCUPADO = 'Ocupado'
    MANTENIMIENTO = 'Mantenimiento'


class EstadoTicket(Enum):
    RESERVADO = 'Reservado'
    USADO = 'Usado'


class Clientes(models.Model):
    clienteid = models.AutoField(primary_key=True, verbose_name='ID')
    nombre = models.CharField(max_length=50, verbose_name='Nombre')
    apellido = models.CharField(max_length=50, verbose_name='Apellido')
    correoelectronico = models.CharField(
        max_length=100, unique=True, default='', verbose_name='Correo Electrónico')
    telefono = models.CharField(
        max_length=15, blank=True, null=True, verbose_name='Teléfono')
    direccion = models.CharField(
        max_length=100, blank=True, null=True, verbose_name='Dirección')
    usuarioid = models.OneToOneField(
        'Usuarios', models.DO_NOTHING, db_column='usuarioid', blank=True, null=True, verbose_name='ID de Usuario')

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    class Meta:
        app_label = 'myapp'
        db_table = 'clientes'


class ClienteFormaDePago(models.Model):
    cliente = models.ForeignKey(Clientes, on_delete=models.CASCADE)
    pago_realizado = models.BooleanField(
        default=False, verbose_name='Pago Realizado')
    stripe_checkout_id = models.CharField(
        max_length=100, verbose_name='ID de Stripe Checkout')

    class Meta:
        verbose_name = 'Cliente Forma de Pago'
        verbose_name_plural = 'Clientes Forma de Pago'
        db_table = 'clienteformadepago'

    def __str__(self):
        return f"Cliente: {self.cliente}, Pago Realizado: {self.pago_realizado}"


@receiver(post_save, sender=Clientes)
def crear_metodo_pago(sender, instance, created, **kwargs):
    if created:
        ClienteFormaDePago.objects.create(cliente=instance)


class Conductores(models.Model):
    conductorid = models.AutoField(primary_key=True, verbose_name='ID')
    nombre = models.CharField(max_length=50, verbose_name='Nombre')
    apellido = models.CharField(max_length=50, verbose_name='Apellido')
    licenciaconducir = models.CharField(
        max_length=20, verbose_name='No. de Licencia')
    telefono = models.CharField(
        max_length=15, blank=True, null=True, verbose_name='Teléfono')
    direccion = models.CharField(
        max_length=100, blank=True, null=True, verbose_name='Dirección')
    fechacontratacion = models.DateField(
        blank=True, null=True, verbose_name='Fecha de Contratación')
    usuarioid = models.OneToOneField(
        'Usuarios', models.DO_NOTHING, db_column='usuarioid', blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.licenciaconducir})"

    class Meta:
        app_label = 'myapp'
        db_table = 'conductores'


class Roles(models.Model):
    rolid = models.AutoField(primary_key=True, verbose_name='ID')
    nombrerol = models.CharField(max_length=50, verbose_name='Nombre')

    class Meta:
        app_label = 'myapp'
        db_table = 'roles'


class Rutas(models.Model):
    rutaid = models.AutoField(primary_key=True, verbose_name='ID')
    origen = models.CharField(max_length=100, verbose_name='Origen')
    destino = models.CharField(max_length=100, verbose_name='Destino')
    distancia = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='Distancia del viaje')
    duracionestimada = models.DurationField(verbose_name='Duración estimada')
    preciobase = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='Precio base de la ruta')

    def __str__(self):
        return f"{self.origen} - {self.destino}"

    class Meta:
        app_label = 'myapp'
        db_table = 'rutas'


class Tickets(models.Model):
    ticketid = models.AutoField(primary_key=True, verbose_name='ID')
    clienteid = models.ForeignKey(
        Clientes, models.DO_NOTHING, db_column='clienteid', verbose_name='ID del Cliente')
    viajeid = models.ForeignKey(
        'Viajes', models.CASCADE, blank=True, null=True, db_column='viajeid', verbose_name='ID del Viaje')
    fechareservacion = models.DateTimeField(
        blank=True, null=True, default=timezone.now, verbose_name='Fecha de Reservación')
    estado_opciones = [(estado.value, estado.name)
                       for estado in EstadoTicket]
    estadoticket = models.CharField(
        max_length=10, blank=True, null=True, choices=estado_opciones, default=EstadoTicket.RESERVADO.value, verbose_name='Estado')
    preciototal = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='Valor Total del Ticket')

    def actualizar_estado(self):
        if self.viajeid is not None:
            fecha_llegada_viaje = self.viajeid.fechahorallegadaestimada
            if self.fechareservacion > fecha_llegada_viaje:
                self.estadoticket = EstadoTicket.USADO.value
                self.save()

    class Meta:
        app_label = 'myapp'
        db_table = 'tickets'


class Usuarios(AbstractBaseUser):
    usuarioid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, verbose_name='ID')
    nombreusuario = models.CharField(
        max_length=50, unique=True, verbose_name='Nombre de usuario')
    password = models.CharField(
        max_length=128, verbose_name='Contraseña', db_column='contraseña')
    estado = models.CharField(
        max_length=10, blank=True, null=True, default='Activo', verbose_name='Estado')
    rolid = models.ForeignKey(Roles, models.DO_NOTHING,
                              db_column='rolid', verbose_name='ID del Rol')
    fechacreacion = models.DateTimeField(
        auto_now_add=True, verbose_name='Fecha de creación')

    objects = CustomUsuarioManager()

    USERNAME_FIELD = 'nombreusuario'
    REQUIRED_FIELDS = ['rolid']

    def __str__(self):
        return self.nombreusuario

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.rolid.nombrerol == 'Administrador'

    class Meta:
        app_label = 'myapp'
        db_table = 'usuarios'


class Vehiculos(models.Model):
    vehiculoid = models.AutoField(primary_key=True, verbose_name='ID')
    modelo = models.CharField(max_length=50, verbose_name='Modelo')
    marca = models.CharField(max_length=50, verbose_name='Marca')
    capacidad = models.IntegerField(
        blank=True, null=True, verbose_name='Capacidad')
    anofabricacion = models.IntegerField(
        blank=True, null=True, verbose_name='Año de Fabriación')
    placa = models.CharField(unique=True, max_length=20,
                             blank=True, null=True, verbose_name='No. de Placa')
    estado_opciones = [(estado.value, estado.name)
                       for estado in EstadoVehiculo]
    estado = models.CharField(
        max_length=15, blank=True, null=True, choices=estado_opciones, default=EstadoVehiculo.DISPONIBLE.value, verbose_name='Estado')
    conductorid = models.ForeignKey(
        Conductores, models.DO_NOTHING, db_column='conductorid', blank=True, null=True, verbose_name='ID del Conductor')

    def __str__(self):
        return f"{self.modelo} {self.marca} del {self.anofabricacion} ({self.placa})"

    class Meta:
        app_label = 'myapp'
        db_table = 'vehiculos'


class Viajes(models.Model):
    viajeid = models.AutoField(primary_key=True, verbose_name='ID')
    rutaid = models.ForeignKey(
        Rutas, models.DO_NOTHING, db_column='rutaid', verbose_name='ID de Ruta')
    vehiculoid = models.ForeignKey(
        Vehiculos, models.DO_NOTHING, blank=True, null=True, db_column='vehiculoid', verbose_name='ID de Vehiculo')
    fechahorasalida = models.DateTimeField(
        verbose_name='Hora de salida del viaje')
    fechahorallegadaestimada = models.DateTimeField(
        verbose_name='Hora estimada de llegada del viajes')
    cuposdisponibles = models.IntegerField(
        verbose_name='Tickets disponibles para viaje')

    class Meta:
        app_label = 'myapp'
        db_table = 'viajes'


def generar_nombre_usuario(nombre, apellido):
    semilla = uuid.uuid4()
    sufijo = str(semilla)[:5]
    usuario = nombre.split()[0] + apellido.split()[0][0]
    return f'{usuario}#{sufijo}'
