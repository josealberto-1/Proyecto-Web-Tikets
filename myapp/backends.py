from django.contrib.auth.backends import BaseBackend
from .models import Usuarios, Clientes


class CustomAuthBackend(BaseBackend):
    def authenticate(nombre_usuario=None, contraseña=None):
        try:
            if "@" in nombre_usuario:
                cliente = Clientes.objects.get(
                    correoelectronico=nombre_usuario)
                usuario = Usuarios.objects.get(nombreusuario=cliente.usuarioid)
            else:
                usuario = Usuarios.objects.get(nombreusuario=nombre_usuario)
            if usuario.check_password(contraseña):
                return usuario
        except (Usuarios.DoesNotExist, Clientes.DoesNotExist):
            return None
