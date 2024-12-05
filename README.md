# OnRoad

<div class="logo" align="center">
    <img src="https://onroad.sirv.com/Images/Logo-no-background.png" width="300" height="300" alt="Logo de la Compañia" style="margin-bottom: 5px;">
</div>

"OnRoad" es una aplicación web desarrollada con Django que ofrece funcionalidades relacionadas con pagos en línea a través de Stripe, un sistema intermediario de pagos online. La aplicación permite a los usuarios realizar pagos de forma segura utilizando la integración de Stripe, lo que proporciona una experiencia fluida y confiable para los clientes.

Además de las funcionalidades de pago, "OnRoad" puede incluir características adicionales relacionadas con la gestión de información de usuarios, como la creación de cuentas, la gestión de perfiles de usuario, entre otras.

## Configuración del Entorno

### Requisitos Previos

Asegúrate de tener instalado lo siguiente:

- Python (versión 3.11)

### Instalación

1. Crear un directorio para el repositorio:

```sh
mkdir Proyecto
cd Proyecto
```

2. Navega al directorio del proyecto:

```sh
cd OnRoad
```

3. Instalar el entorno virtual con el intérprete a usar:

```sh
pip install virtualenv -t "/ruta/del/intérprete"
```

4. Inicializar el entorno virtual:

```sh
.\.venv\Scripts\activate
```

5. Clonar el repositorio:

```sh
git clone https://github.com/GuilleAQN/OnRoad.git
```

6. Instala las dependencias principales:

```sh
pip install -r requirements.txt
```

En caso de querer desarrollar, instala las dependencias de desarrollo:

```sh
pip install -r requirements.dev.txt
```

Nota: Para esto, descargar [Stripe CLI](https://docs.stripe.com/stripe-cli), y usar la **STRIPE_SECRET_KEY** y la **STRIPE_PUBLIC_KEY** en un archivo ".env", y seguir la documentación de Stripe para correr este proyecto en local.

7. Clonar el archivo de las variables de entorno:

```sh
copy .env.example .env
```

Aqui es necesario configurar las siguientes variables:

- `APP_ENV`: Define el entorno en el que se ejecuta la aplicación. Los valores posibles son:
    - `production`: Para el entorno de producción.
    - `development`: Para el entorno de desarrollo.

- `DATABASE_DEV_URL`: URL de conexión a la base de datos en desarrollo. 

- `DATABASE_PROD_URL`: URL de conexión a la base de datos en producción. Usa el mismo formato que el de desarrollo.

- `STRIPE_SECRET_KEY` y `STRIPE_PUBLIC_KEY`: Claves para la integración con Stripe.
   - La clave secreta (`STRIPE_SECRET_KEY`) se utiliza para operaciones internas con Stripe.
   - La clave pública (`STRIPE_PUBLIC_KEY`) es para el cliente.

- `EMAIL`: Dirección de correo electrónico utilizada por la aplicación para notificaciones o mensajes.

- `EMAIL_PASSWORD`: Contraseña de la cuenta de correo configurada.

8. Aplica las migraciones de la base de datos:

```sh
python manage.py migrate
```

9. Aplica el ingreso de la data inicial a la base de datos:

```sh
python manage.py seed_data
```

10. Crea un usuario de pruebas:

```sh
python manage.py createsuperuser
```

11. Ejecuta el servidor de desarrollo:

```sh
python manage.py runserver 3000
```

La aplicación estará disponible en `http://localhost:3000/`.

## Uso

## Stack Tecnológico

- **Django**: Framework web de Python.
- **Stripe**: Sistema intermediario de pagos online.
- **Bootstrap**: Framework CSS para desarrollo web responsivo.
- **PostgreSQL**: Sistema de gestión de bases de datos relacional.
- **Render**: Servicio de hosting para aplicaciones web.

[![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Bootstrap](https://img.shields.io/badge/bootstrap-%238511FA.svg?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Render](https://img.shields.io/badge/Render-%46E3B7.svg?style=for-the-badge&logo=render&logoColor=white)](https://render.com/)
[![Stripe](https://img.shields.io/badge/Stripe-5469d4?style=for-the-badge&logo=stripe&logoColor=ffffff)](https://stripe.com/es)

## Contribución

<div align="center">

![Alt](https://repobeats.axiom.co/api/embed/9fb7aa265e4f231795d36f7dc828451fcb4f9738.svg "Repobeats analytics image")

</div>

Si deseas contribuir al proyecto, sigue estos pasos:

1. Haz un fork del repositorio.
2. Crea una rama para tu funcionalidad (`git checkout -b feature/NuevoFeature`).
3. Haz commit de tus cambios (`git commit -m 'feat: Añadir un NuevoFeature'`).
4. Sube tus cambios (`git push origin feature/NuevoFeature`).
5. Abre un pull request.

## Contacto

Si tienes preguntas, comentarios o sugerencias sobre "OnRoad", no dudes en ponerte en contacto:

- **Nombre**: Jose Alberto Medina (Back-End) y Daniel de la Rosa (Front-End).
- **Correo Electrónico**: [jm20-0441@unphu.edu.do](mailto:jm20-0441@unphu.edu.do) y [dd21-1799@unphu.edu.do](mailto:dd21-1799@unphu.edu.do)

También puedes abrir un problema en el repositorio de GitHub si encuentras algún error o deseas solicitar una nueva característica.
