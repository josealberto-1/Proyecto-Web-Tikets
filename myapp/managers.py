from django.contrib.auth.base_user import BaseUserManager
from django.forms import ValidationError


class CustomUsuarioManager(BaseUserManager):
    def create_user(self, nombreusuario, contraseña, rolid=None, **extra_fields):
        if not nombreusuario:
            raise ValueError("El nombre de usuario debe ser definido.")
        
        if not rolid and not extra_fields.get("is_staff", False):
            raise ValidationError(
                "El rol del usuario es requerido para usuarios que no son administradores."
            )

        from myapp.models import Roles


        if isinstance(rolid, int):
            try:
                rolid = Roles.objects.get(pk=rolid)
            except Roles.DoesNotExist:
                raise ValueError("El rol especificado no existe.")

        user = self.model(nombreusuario=nombreusuario, rolid=rolid, **extra_fields)
        user.set_password(contraseña)
        user.save(using=self._db)
        return user

    def create_superuser(self, nombreusuario, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("El superusuario debe tener is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("El superusuario debe tener is_superuser=True.")

        return self.create_user(nombreusuario, password, rolid=1, **extra_fields)
