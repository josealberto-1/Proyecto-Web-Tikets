from django.core.management.base import BaseCommand
from myapp.models import Usuarios, Conductores, Vehiculos

class Command(BaseCommand):
    help = 'Elimina un usuario por su nombre de usuario'

    def add_arguments(self, parser):
        parser.add_argument('nombreusuario', type=str, help='Nombre del usuario que deseas eliminar')

    def handle(self, *args, **kwargs):
        nombreusuario = kwargs['nombreusuario']
        try:
            user = Usuarios.objects.get(nombreusuario=nombreusuario)

            # Obtén el conductor asociado al usuario
            conductor = Conductores.objects.filter(usuarioid=user)

            # Elimina los vehículos relacionados al conductor
            Vehiculos.objects.filter(conductorid__in=conductor).delete()

            # Elimina los conductores relacionados al usuario
            conductor.delete()

            # Finalmente, elimina el usuario
            user.delete()

            self.stdout.write(self.style.SUCCESS(f"Usuario '{nombreusuario}' eliminado exitosamente."))
        except Usuarios.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"El usuario '{nombreusuario}' no existe."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error al eliminar el usuario: {e}"))
