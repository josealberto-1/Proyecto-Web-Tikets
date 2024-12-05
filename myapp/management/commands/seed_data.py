from myapp.models import Roles, Usuarios
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Seed initial data"

    def handle(self, *args, **kwargs):
        # Create roles
        Roles.objects.bulk_create(
            [
                Roles(rolid=1, nombrerol="Administrador"),
                Roles(rolid=2, nombrerol="Cliente"),
                Roles(rolid=3, nombrerol="Conductor"),
            ]
        )

        # Create admin user
        Usuarios.objects.create_superuser(
            username="admin", email="admin@example.com", password="admin123", rol_id=1
        )

        self.stdout.write(
            self.style.SUCCESS("Successfully seeded roles and admin user!")
        )
