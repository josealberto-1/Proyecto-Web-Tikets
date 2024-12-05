from django import forms
from django.contrib.auth.hashers import make_password
from .models import Usuarios, Roles, Conductores, Clientes, Rutas, Vehiculos, Viajes, EstadoVehiculo


class SignInForm(forms.Form):
    usuario = forms.CharField(widget=forms.TextInput(
        attrs={'id': 'usuario', 'class': 'form-control', 'placeholder': 'Introduzca su usuario o correo', 'autocomplete': 'email'}))
    contraseña = forms.CharField(widget=forms.PasswordInput(
        attrs={'id': 'contraseña', 'class': 'form-control', 'placeholder': 'Introduzca su contraseña'}))


class SignUpForm(forms.ModelForm):
    confirmar_contraseña = forms.CharField(widget=forms.PasswordInput(
        attrs={'id': 'contraseñaConfirmacion', 'class': 'form-control', 'placeholder': 'Repita su contraseña'}))

    class Meta:
        model = Usuarios
        fields = ['password', ]
        widgets = {
            'password': forms.PasswordInput(attrs={'id': 'contraseña', 'class': 'form-control', 'placeholder': 'Introduzca su contraseña'}),
        }

    def clean(self):
        data_limpia = super().clean()
        contraseña = data_limpia.get('password')
        confirmar_contraseña = data_limpia.get('confirmar_contraseña')

        if contraseña != confirmar_contraseña:
            raise forms.ValidationError("Las contraseñas no coinciden.")

        return data_limpia

    def save(self, commit=True, rol=1):
        usuario = super().save(commit=False)
        usuario.rolid = Roles.objects.get(rolid=rol)
        usuario.password = make_password(self.clean()['password'])
        if commit:
            usuario.save()
        return usuario


class NuevoUsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuarios
        fields = ['password']
        widgets = {
            'password': forms.PasswordInput(attrs={'id': 'contraseña', 'class': 'form-control', 'placeholder': 'Introduzca su contraseña'}),
        }

    def save(self, commit=True, rol=1):
        usuario = super().save(commit=False)
        usuario.rolid = Roles.objects.get(rolid=rol)
        usuario.password = make_password(self.clean()['password'])
        if commit:
            usuario.save()
        return usuario


class NuevoAdminForm(forms.ModelForm):
    class Meta:
        model = Usuarios
        fields = ['nombreusuario', 'password']
        widgets = {
            'nombreusuario': forms.TextInput(attrs={'id': 'usuario', 'class': 'form-control', 'placeholder': 'Introduzca su usuario'}),
            'password': forms.PasswordInput(attrs={'id': 'contraseña', 'class': 'form-control', 'placeholder': 'Introduzca su contraseña'}),
        }

    def save(self, commit=True):
        admin = super().save(commit=False)
        admin.rolid = Roles.objects.get(rolid=1)
        admin.password = make_password(self.clean()['password'])
        if commit:
            admin.save()
        return admin


class NuevoClienteForm(forms.ModelForm):
    class Meta:
        model = Clientes
        fields = ['nombre', 'apellido', 'correoelectronico', 'telefono',
                  'direccion']
        widgets = {
            'nombre': forms.TextInput(attrs={'id': 'nombre', 'class': 'form-control', 'placeholder': 'Introduzca su nombre'}),
            'apellido': forms.TextInput(attrs={'id': 'apellido', 'class': 'form-control', 'placeholder': 'Introduzca su apellido'}),
            'correoelectronico': forms.EmailInput(attrs={'id': 'correoElectronico', 'class': 'form-control', 'placeholder': 'Introduzca su correo electrónico'}),
            'telefono': forms.TextInput(attrs={'id': 'telefono', 'class': 'form-control', 'placeholder': 'Introduzca su teléfono'}),
            'direccion': forms.TextInput(attrs={'id': 'direccion', 'class': 'form-control', 'placeholder': 'Introduzca su dirección'}),
        }

    def save(self, commit=True, usuario=None):
        cliente = super().save(commit=False)
        if usuario is not None:
            cliente.usuarioid = usuario
            if commit:
                cliente.save()
        return cliente


class NuevoConductorForm(forms.ModelForm):
    class Meta:
        model = Conductores
        fields = ['nombre', 'apellido', 'licenciaconducir', 'telefono',
                  'direccion', 'fechacontratacion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'id': 'nombre',
                'class': 'form-control',
                'placeholder': 'Introduzca el nombre'
            }),
            'apellido': forms.TextInput(attrs={
                'id': 'apellido',
                'class': 'form-control',
                'placeholder': 'Introduzca el apellido'
            }),
            'licenciaconducir': forms.TextInput(attrs={
                'id': 'licencia',
                'class': 'form-control',
                'placeholder': 'Introduzca la licencia de conducir'
            }),
            'telefono': forms.TextInput(attrs={
                'id': 'telefono',
                'class': 'form-control',
                'placeholder': 'Introduzca el teléfono'
            }),
            'direccion': forms.TextInput(attrs={
                'id': 'direccion',
                'class': 'form-control',
                'placeholder': 'Introduzca su dirección'
            }),
            'fechacontratacion': forms.DateInput(attrs={
                'id': 'fechaDeContratacion',
                'class': 'form-control',
                'type': 'date',
                'placeholder': 'dd/mm/aaaa'
            }),
        }

    def clean(self):
        data_limpia = super().clean()
        fecha_contratacion = data_limpia.get('fechacontratacion')
        
        if not fecha_contratacion:
            instance = getattr(self, 'instance', None)
            if instance:
                data_limpia['fechacontratacion'] = instance.fechacontratacion
        
        return data_limpia

    def save(self, commit=True, usuario=None):
        conductor = super().save(commit=False)
        if usuario is not None:
            conductor.usuarioid = usuario
        if commit:
            conductor.save()
        return conductor


class NuevoViajesForm(forms.ModelForm):
    class Meta:
        model = Viajes
        fields = ['rutaid', 'vehiculoid',
                  'fechahorasalida', 'fechahorallegadaestimada']
        widgets = {
            'rutaid': forms.Select(attrs={
                'id': 'rutas',
                'class': 'form-control',
            }),
            'vehiculoid': forms.Select(attrs={
                'id': 'vehiculos',
                'class': 'form-control',
            }),
            'fechahorasalida': forms.DateTimeInput(attrs={
                'id': 'fechaHoraSalida',
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'fechahorallegadaestimada': forms.DateTimeInput(attrs={
                'id': 'fechaHoraLlegada',
                'class': 'form-control',
                'type': 'datetime-local'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vehiculoid'].queryset = Vehiculos.objects.filter(
            estado=EstadoVehiculo.DISPONIBLE.value)

    def clean(self):
        data_limpia = super().clean()
        fechahorasalida = data_limpia.get('fechahorasalida')
        fechahorallegadaestimada = data_limpia.get('fechahorasalida')
        
        if not fechahorasalida:
            instance = getattr(self, 'instance', None)
            if instance:
                data_limpia['fechahorasalida'] = instance.fechahorasalida

        if not fechahorallegadaestimada:
            instance = getattr(self, 'instance', None)
            if instance:
                data_limpia['fechahorallegadaestimada'] = instance.fechahorallegadaestimada

        return data_limpia


    def save(self, commit=True):
        viaje = super().save(commit=False)
        viaje.cuposdisponibles = viaje.vehiculoid.capacidad
        if commit:
            viaje.save()
        return viaje


class NuevoVehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculos
        fields = ['modelo', 'marca', 'capacidad',
                  'anofabricacion', 'placa', 'estado', 'conductorid']
        widgets = {
            'modelo': forms.TextInput(attrs={
                'id': 'modelo',
                'class': 'form-control',
                'placeholder': 'Introduzca el modelo'
            }),
            'marca': forms.TextInput(attrs={
                'id': 'marca',
                'class': 'form-control',
                'placeholder': 'Introduzca la marca'
            }),
            'capacidad': forms.NumberInput(attrs={
                'id': 'capacidad',
                'class': 'form-control',
                'min': 0,
                'placeholder': 'Introduzca la cantidad'
            }),
            'anofabricacion': forms.NumberInput(attrs={
                'id': 'añoFabricacion',
                'class': 'form-control',
                'min': 1990,
                'placeholder': 'Introduzca el año'
            }),
            'placa': forms.TextInput(attrs={
                'id': 'placa',
                'class': 'form-control',
                'placeholder': 'Introduzca la placa'
            }),
            'estado': forms.Select(attrs={
                'id': 'estado',
                'class': 'form-control',
            }),
            'conductorid': forms.Select(attrs={
                'id': 'conductores',
                'class': 'form-control',
            }),
        }


class NuevaRutaForm(forms.ModelForm):
    class Meta:
        model = Rutas
        fields = ['origen', 'destino', 'distancia',
                  'duracionestimada', 'preciobase']
        widgets = {
            'origen': forms.TextInput(attrs={
                'id': 'origen',
                'class': 'form-control',
                'placeholder': 'Introduzca el origen'
            }),
            'destino': forms.TextInput(attrs={
                'id': 'destino',
                'class': 'form-control',
                'placeholder': 'Introduzca el destino'
            }),
            'distancia': forms.NumberInput(attrs={
                'id': 'distancia',
                'class': 'form-control',
                'min': 0,
                'placeholder': 'Introduzca la distancia'
            }),
            'duracionestimada': forms.TimeInput(attrs={
                'id': 'duracionEstimada',
                'class': 'form-control',
                'type': 'time'
            }),
            'preciobase': forms.NumberInput(attrs={
                'id': 'precioBase',
                'class': 'form-control',
                'min': 0,
                'value': 0,
                'step': .01,
                'placeholder': 'Introduzca el precio'
            }),
        }
