from django.contrib.auth.management.commands.createsuperuser import (
    Command as BaseCreateSuperUserCommand,
)
from django.core.management.base import CommandError


class Command(BaseCreateSuperUserCommand):
    help = "Crea un superusuario con rol predeterminado."

    def handle(self, *args, **options):
        options["rolid"] = options.get("rolid", 1)

        try:
            super().handle(*args, **options)
        except Exception as e:
            raise CommandError(f"Error al crear el superusuario: {e}")
