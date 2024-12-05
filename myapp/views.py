import os
import json
import time
import stripe
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponse
from django.db import transaction
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from mysite.settings import BASE_DIR
from .backends import CustomAuthBackend
from .models import Usuarios, Clientes, Conductores, Vehiculos, Rutas, Viajes, Roles, Tickets, ClienteFormaDePago, generar_nombre_usuario
from .forms import SignInForm, SignUpForm, NuevoUsuarioForm, NuevoAdminForm, NuevoClienteForm, NuevoConductorForm,  NuevoViajesForm, NuevoVehiculoForm, NuevaRutaForm


def signin(request):
    if request.method == "GET":
        form = SignInForm()
        return render(request, "signin.html", {"form": form})
    else:
        form = SignInForm(request.POST)
        if form.is_valid():
            usuario = form.cleaned_data['usuario']
            contraseña = form.cleaned_data['contraseña']
            usuario = CustomAuthBackend.authenticate(
                nombre_usuario=usuario, contraseña=contraseña)
            if usuario is not None:
                login(request, usuario)
                return redirect('pagina_principal')
        messages.error(
            request, 'Las credenciales no son correctas, por favor intente de nuevo.')
        return render(request, "signin.html", {"form": form})


def signup(request):
    if request.method == "GET":
        formUsuario = SignUpForm()
        formCliente = NuevoClienteForm()
        return render(request, "signup.html", {"formUsuario": formUsuario, "formCliente": formCliente})
    else:
        formUsuario = NuevoUsuarioForm(request.POST)
        formCliente = NuevoClienteForm(request.POST)

        if formUsuario.is_valid() and formCliente.is_valid():
            nombre = formCliente.cleaned_data['nombre']
            apellido = formCliente.cleaned_data['apellido']

            nombre_usuario = generar_nombre_usuario(nombre, apellido)

            usuario = formUsuario.save(commit=False, rol=2)
            cliente = formCliente.save(commit=False, usuario=usuario)

            usuario.nombreusuario = nombre_usuario
            usuario.save()
            cliente.save()

            login(request, usuario)
            return redirect('pagina_principal')

        messages.error(
            request, 'Ha ocurrido un error, por favor intente de nuevo.')
        return render(request, "signup.html", {"formUsuario": formUsuario, "formCliente": formCliente})


@login_required
def pagina_principal(request):
    rol = "bases/baseadmin.html" if request.user.rolid.rolid == 1 else (
        "bases/base.html" if request.user.rolid.rolid == 2 else "bases/baseconductor.html")

    return render(request, "index.html", {
        'rol': rol,
        'usuario': request.user
    })


@login_required
def signout(request):
    logout(request)
    return redirect('signin')


@login_required
def see_perfil(request):
    rol = "bases/base.html" if request.user.rolid.rolid == 2 else "bases/baseconductor.html"
    try:
        datos_usuario = Clientes.objects.get(usuarioid=request.user.usuarioid)
    except Clientes.DoesNotExist:
        datos_usuario = Conductores.objects.get(
            usuarioid=request.user.usuarioid)
    return render(request, "perfil.html", {"rol": rol, "usuario": request.user, "datos": datos_usuario})


@login_required
def elegir_usuario(request):
    roles = Roles.objects.all()
    return render(request, "admin/elegir_usuario.html", {"roles": roles, "usuario": request.user})


@login_required
def create_usuario(request):
    rol = request.GET.get('inputRoles')
    if request.method == "GET":
        if rol == '1':
            form = NuevoAdminForm()
        elif rol == '2':
            formUsuario = NuevoUsuarioForm()
            formCliente = NuevoClienteForm()
        else:
            formUsuario = NuevoUsuarioForm()
            formConductor = NuevoConductorForm()

        return render(request, "admin/create_usuario.html", {
            "usuario": request.user,
            "rol": rol,
            "form": form if rol == '1' else None,
            "formUsuario": formUsuario if rol == '2' or rol == '3' else None,
            "formCliente": formCliente if rol == '2' else None,
            "formConductor": formConductor if rol != '1' and rol != '2' else None
        })

    else:
        if request.GET.get('rol') == '1':
            form = NuevoAdminForm(request.POST)
            if form.is_valid():
                form.save()

                messages.success(
                    request, 'Se ha registrado el usuario de manera exitosa.')
                return redirect('rol_usuario')

        if request.GET.get('rol') == '2':
            formUsuario = NuevoUsuarioForm(request.POST)
            formCliente = NuevoClienteForm(request.POST)

            if formUsuario.is_valid() and formCliente.is_valid():
                nombre = formCliente.cleaned_data['nombre']
                apellido = formCliente.cleaned_data['apellido']

                nombre_usuario = generar_nombre_usuario(
                    nombre=nombre, apellido=apellido)

                cliente = formCliente.save(commit=False)
                usuario = formUsuario.save(commit=False, rol=2)

                usuario.nombreusuario = nombre_usuario
                cliente.save()
                usuario.save()

                messages.success(
                    request, 'Se ha registrado el usuario de manera exitosa.')
                return redirect('rol_usuario')

        else:
            formUsuario = NuevoUsuarioForm(request.POST)
            formConductor = NuevoConductorForm(request.POST)

            if formUsuario.is_valid() and formConductor.is_valid():
                nombre = formConductor.cleaned_data['nombre']
                apellido = formConductor.cleaned_data['apellido']

                nombre_usuario = generar_nombre_usuario(nombre, apellido)

                informacion = {
                    "nombre_completo": formConductor.cleaned_data['nombre'] + " " + formConductor.cleaned_data['apellido'],
                    "usuario": nombre_usuario,
                    "contraseña": formUsuario.cleaned_data['password'],
                }

                usuario = formUsuario.save(commit=False, rol=3)
                conductor = formConductor.save(commit=False, usuario=usuario)

                usuario.nombreusuario = nombre_usuario
                usuario.save()
                conductor.save()

                template_name = BASE_DIR/"myapp/templates/email/conductor_respuesta.html"
                html_contenido = render_to_string(
                    template_name=template_name,
                    context=informacion
                )
                mensaje_plano = strip_tags(html_contenido)

                send_mail(
                    subject="Bienvenido a la Familia de OnRoad",
                    message=mensaje_plano,
                    recipient_list=[request.POST.get('correo_envio')],
                    from_email=None,
                    html_message=html_contenido,
                    fail_silently=False
                )

                messages.success(
                    request, 'Se ha registrado el usuario de manera exitosa.')
                return redirect('rol_usuario')

        messages.error(
            request, 'Ha ocurrido un error, por favor intente de nuevo')
        return redirect('rol_usuario')


@login_required
def create_ruta(request):
    if request.method == "GET":
        form = NuevaRutaForm()
        return render(request, "admin/create_ruta.html", {'form': form, 'usuario': request.user})
    else:
        form = NuevaRutaForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request, 'Se ha registrado la ruta de manera exitosa.')

            return redirect('pagina_principal')

        messages.error(
            request, 'Ha ocurrido un error, por favor intente de nuevo.')
        return redirect('nueva_ruta')


@login_required
def create_vehiculo(request):
    if request.method == "GET":
        form = NuevoVehiculoForm()
        return render(request, "admin/create_vehiculo.html", {"form": form, 'usuario': request.user})
    else:
        formVehiculo = NuevoVehiculoForm(request.POST)
        if formVehiculo.is_valid():
            formVehiculo.save(commit=False)
            formVehiculo.save()

            messages.success(
                request, 'Se ha registrado el vehiculo de manera exitosa.')
            return redirect('registro_vehiculo')

        messages.error(
            request, 'Ha ocurrido un error, por favor intente de nuevo.')
        return redirect('registro_vehiculo')


@login_required
def create_viaje(request):
    if request.method == "GET":
        form = NuevoViajesForm()
        return render(request, "admin/create_viaje.html", {"form": form, 'usuario': request.user})
    else:
        formViaje = NuevoViajesForm(request.POST)
        if formViaje.is_valid():
            formViaje.save(commit=False)
            formViaje.save()

            messages.success(
                request, 'Se ha registrado el viaje de manera exitosa.')
            return redirect('registro_viaje')

        messages.error(
            request, 'Ha ocurrido un error, por favor intente de nuevo.')
        return redirect('registro_viaje')


@login_required
def create_ruta(request):
    if request.method == "GET":
        form = NuevaRutaForm()
        return render(request, "admin/create_ruta.html", {"form": form, 'usuario': request.user})
    else:
        formRuta = NuevaRutaForm(request.POST)
        if formRuta.is_valid():
            formRuta.save(commit=False)
            formRuta.save()

            messages.success(
                request, 'Se ha registrado el viaje de manera exitosa.')
            return redirect('registro_viaje')

        messages.error(
            request, 'Ha ocurrido un error, por favor intente de nuevo.')
        return redirect('registro_viaje')


@login_required
def buy_ticket(request):
    if request.method == "GET":
        cliente = Clientes.objects.get(usuarioid=request.user.usuarioid)
        viajes_del_cliente = Tickets.objects.filter(
            clienteid=cliente).values_list('viajeid', flat=True)

        fecha = timezone.now()
        viajes = Viajes.objects.filter(
            fechahorasalida__gte=str(fecha)).exclude(viajeid__in=viajes_del_cliente)

        return render(request, "venta_ticket.html", {"viajes": viajes, 'usuario': request.user})
    else:
        viaje_id = request.POST.get('id')
        viaje = Viajes.objects.get(viajeid=viaje_id)
        precio_base_viaje = int(viaje.rutaid.preciobase)

        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

        url_base = request.build_absolute_uri(reverse('pago_satisfactorio'))

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'dop',
                        'unit_amount': precio_base_viaje * 100,
                        'product_data': {
                            'name': f'Ruta de viaje: {viaje.rutaid.origen} - {viaje.rutaid.destino}',
                        },
                    },
                    'quantity': 1,
                },
            ],
            customer_creation='always',
            mode='payment',
            success_url=url_base +
            '?session_id={CHECKOUT_SESSION_ID}' + f'&viajeid={viaje_id}',
            cancel_url=request.build_absolute_uri(reverse('pago_cancelado'))
        )

        return redirect(checkout_session.url, code=303)


@login_required
def succesful_pay(request):
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

    checkout_session_id = request.GET.get('session_id')
    viaje_id = request.GET.get('viajeid')

    try:
        sesion = stripe.checkout.Session.retrieve(checkout_session_id)
    except stripe.error.InvalidRequestError as e:
        messages.error(
            request, 'La sesión de pago proporcionada no es válida.')
        return redirect('comprar_ticket')

    cliente_credenciales = get_object_or_404(
        Clientes, usuarioid=request.user.usuarioid)

    cliente_pago, creado = ClienteFormaDePago.objects.get_or_create(
        cliente=cliente_credenciales)
    cliente_pago.stripe_checkout_id = checkout_session_id
    cliente_pago.save()

    with transaction.atomic():
        try:
            viaje = Viajes.objects.select_for_update().get(viajeid=viaje_id)
            if viaje.cuposdisponibles > 0:
                viaje.cuposdisponibles -= 1
                viaje.save()
                ticket = Tickets.objects.create(
                    clienteid=cliente_credenciales, viajeid=viaje, preciototal=viaje.rutaid.preciobase)

                ticket_detalle = Tickets.objects.get(ticketid=ticket.ticketid)

                informacion = {
                    "nombre_completo": f"{cliente_pago.cliente.nombre} {cliente_pago.cliente.apellido}",
                    "viaje": f"{ticket_detalle.viajeid.fechahorasalida} - {ticket_detalle.viajeid.fechahorallegadaestimada}",
                    "fecha": ticket_detalle.fechareservacion,
                    "precio": ticket_detalle.preciototal,
                }

                template_name = BASE_DIR/"myapp/templates/email/compra_ticket_respuesta.html"
                html_contenido = render_to_string(
                    template_name=template_name,
                    context=informacion
                )
                mensaje_plano = strip_tags(html_contenido)

                send_mail(
                    subject="Compra de Ticket Aprovada | OnRoad",
                    message=mensaje_plano,
                    recipient_list=[cliente_pago.cliente.correoelectronico],
                    from_email=None,
                    html_message=html_contenido,
                    fail_silently=False
                )
                messages.success(
                    request, 'Se ha comprado el boleto exitosamente.')
            else:
                messages.error(
                    request, 'No hay cupos disponibles para este viaje.')
        except Viajes.DoesNotExist:
            messages.error(request, 'El viaje especificado no existe.')

    return redirect('comprar_ticket')


@login_required
def cancelled_pay(request):
    messages.error(request, 'Saldo insuficiente para comprar el boleto.')
    return redirect('comprar_ticket')


@login_required
def see_rutas(request):
    rutas = Rutas.objects.all()
    return render(request, "admin/view_rutas.html", {'rutas': rutas, 'usuario': request.user})


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    event = None
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
    time.sleep(10)

    try:
        event = stripe.Event.construct_from(
            json.loads(payload), stripe.api_key
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event.type == 'checkout.session.completed':
        sesion = event['data']['object']
        id_sesion = sesion.get('id', None)
        time.sleep(10)

        cliente_pago = ClienteFormaDePago.objects.get(
            stripe_checkout_id=id_sesion)

        cliente_pago.pago_realizado = True
        cliente_pago.save()
    return HttpResponse(status=200)


@login_required
def my_viajes_completados(request):
    conductor = get_object_or_404(
        Conductores, usuarioid=request.user.usuarioid)
    viajes = Viajes.objects.filter(vehiculoid__conductorid=conductor.conductorid,
                                   fechahorasalida__lt=timezone.now())
    return render(request, "proximos_viajes.html", {'viajes': viajes, 'usuario': request.user})


@login_required
def my_viajes_en_curso(request):
    conductor = get_object_or_404(
        Conductores, usuarioid=request.user.usuarioid)
    viajes = Viajes.objects.filter(vehiculoid__conductorid=conductor.conductorid,
                                   fechahorasalida__gte=timezone.now())
    return render(request, "viajes_completados.html", {'viajes': viajes, 'usuario': request.user})


@login_required
def see_viajes(request):
    viajes = Viajes.objects.all()
    return render(request, "admin/view_viajes.html", {'viajes': viajes, 'usuario': request.user})


@login_required
def see_vehiculos(request):
    vehiculos = Vehiculos.objects.exclude(modelo='Placeholder')
    return render(request, "admin/view_vehiculos.html", {'vehiculos': vehiculos, 'usuario': request.user})


@login_required
def see_tickets(request):
    tickets = Tickets.objects.all()
    return render(request, "admin/view_tickets.html", {"tickets": tickets, 'usuario': request.user})


@login_required
def see_my_tickets(request):
    cliente = Clientes.objects.get(usuarioid=request.user.usuarioid)
    Tickets.actualizar_estado
    tickets = Tickets.objects.filter(clienteid=cliente.clienteid)
    return render(request, "my_tickets.html", {"tickets": tickets, 'usuario': request.user})


@login_required
def see_usuarios(request):
    usuarios = Usuarios.objects.all()
    return render(request, "admin/view_usuarios.html", {'usuarios': usuarios, 'usuario': request.user})


@login_required
def see_conductores(request):
    conductores = Conductores.objects.all()
    return render(request, "admin/view_conductores.html", {'conductores': conductores, 'usuario': request.user})


@login_required
def delete_ruta(request, id):
    ruta = get_object_or_404(Rutas, rutaid=id)
    ruta.delete()
    messages.success(request, 'Se ha eliminado la ruta de manera exitosa.')
    return redirect('ver_rutas')


@login_required
def delete_viaje(request, id):
    viaje = get_object_or_404(Viajes, viajeid=id)
    viaje.delete()
    messages.success(request, 'Se ha eliminado el viaje de manera exitosa.')
    return redirect('ver_viajes')


def delete_vehiculo(request, id):
    vehiculo = get_object_or_404(Vehiculos, vehiculoid=id)
    vehiculo.delete()
    messages.success(request, 'Se ha eliminado el vehículo de manera exitosa.')
    return redirect('ver_vehiculos')


@login_required
def delete_usuario(request, id):
    usuario = get_object_or_404(Usuarios, usuarioid=id)
    if usuario.rolid.rolid == 2:
        cliente = Clientes.objects.get(usuarioid=id)
        try:
            tickets = Tickets.objects.get(clienteid=cliente.clienteid)
            cliente_pago = ClienteFormaDePago.objects.get(cliente=cliente)
            cliente_pago.delete()
            tickets.delete()
        except (Tickets.DoesNotExist):
            pass
        cliente.delete()
    usuario.delete()
    messages.success(request, 'Se ha eliminado el usuario de manera exitosa.')
    return redirect('ver_usuarios')


@login_required
def delete_conductor(request, id):
    conductor = get_object_or_404(Conductores, conductorid=id)
    conductor.delete()
    messages.success(
        request, 'Se ha eliminado el conductor de manera exitosa.')
    return redirect('ver_conductores')


@login_required
def edit_viaje(request, id):
    viaje = get_object_or_404(Viajes, pk=id)

    if request.method == 'GET':
        form = NuevoViajesForm(instance=viaje)
        return render(request, 'admin/create_viaje.html', {'form': form})

    else:
        form = NuevoViajesForm(request.POST, instance=viaje)
        if form.is_valid():
            form.save()
        messages.success(request, 'Se ha editado el viaje de manera exitosa.')
        return redirect('ver_viajes')


@login_required
def edit_ruta(request, id):
    ruta = get_object_or_404(Rutas, pk=id)

    if request.method == 'GET':
        form = NuevaRutaForm(instance=ruta)
        return render(request, 'admin/create_ruta.html', {'form': form})

    else:
        form = NuevaRutaForm(request.POST, instance=ruta)
        if form.is_valid():
            form.save()
        messages.success(request, 'Se ha editado la ruta de manera exitosa.')
        return redirect('ver_rutas')


@login_required
def edit_vehiculo(request, id):
    vehiculo = get_object_or_404(Vehiculos, pk=id)

    if request.method == 'GET':
        form = NuevoVehiculoForm(instance=vehiculo)
        return render(request, 'admin/create_vehiculo.html', {'form': form})

    else:
        form = NuevoVehiculoForm(request.POST, instance=vehiculo)
        if form.is_valid():
            form.save()
        messages.success(
            request, 'Se ha editado el vehiculo de manera exitosa.')
        return redirect('ver_vehiculos')


@login_required
def edit_conductor(request, id):
    conductor = get_object_or_404(Conductores, pk=id)

    if request.method == 'GET':
        form = NuevoConductorForm(instance=conductor)
        return render(request, 'admin/edit_conductor.html', {'form': form, 'usuario': request.user})

    else:
        form = NuevoConductorForm(request.POST, instance=conductor)
        if form.is_valid():
            form.clean()
            form.save()
            messages.success(
                request, 'Se ha editado el conductor de manera exitosa.')
        return redirect('ver_conductores')


@login_required
def edit_usuario(request, id):
    if request.method == 'GET':
        rol = "bases/baseadmin.html" if request.user.rolid.rolid == 1 else (
            "bases/base.html" if request.user.rolid.rolid == 2 else "bases/baseconductor.html")
        try:
            usuario = Clientes.objects.get(usuarioid=id)
            form = NuevoClienteForm(instance=usuario)
        except Clientes.DoesNotExist:
            usuario = get_object_or_404(Conductores, usuarioid=id)
            form = NuevoConductorForm(instance=usuario)

        return render(request, 'edit_usuario.html', {'form': form, 'usuario': request.user, 'rol': rol})

    else:
        try:
            usuario = Clientes.objects.get(usuarioid=request.user.usuarioid)
            form = NuevoClienteForm(request.POST, instance=usuario)
        except Clientes.DoesNotExist:
            usuario = Conductores.objects.get(usuarioid=request.user.usuarioid)
            form = NuevoConductorForm(request.POST, instance=usuario)

        if form.is_valid():
            form.save()

        messages.success(request, 'Se ha editado su perfil de manera exitosa.')
        return redirect('perfil')
