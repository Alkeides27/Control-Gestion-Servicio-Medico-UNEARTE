from django import forms
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from .models import Paciente, TipoDocumento, Genero, Direccion, Telefono, Ciudad, Estado, Pais, TipoTelefono


class PacienteForm(forms.ModelForm):
    confirmar_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Repita el correo electrónico'}),
        label="Confirmar Email"
    )

    class Meta:
        model = Paciente
        fields = [
            'numero_documento',
            'nombre',
            'apellido',
            'fecha_nacimiento',
            'genero',
            'email',
        ]
        widgets = {
            'numero_documento': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '8',
                'placeholder': 'Ej: 12345678'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '30',
                'placeholder': 'Ej: Juan Carlos'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '20',
                'placeholder': 'Ej: García López'
            }),
            'fecha_nacimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'genero': forms.Select(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@correo.com'}),
        }
        labels = {
            'numero_documento': 'Número de Cédula',
            'nombre': 'Nombres',
            'apellido': 'Apellidos',
            'fecha_nacimiento': 'Fecha de Nacimiento',
            'genero': 'Género',
            'email': 'Correo Electrónico',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.instance.pk:
            self.fields['genero'].initial = Genero.MASCULINO

        if self.instance and self.instance.fecha_nacimiento:
            self.fields['fecha_nacimiento'].widget.attrs['value'] = self.instance.fecha_nacimiento.strftime('%Y-%m-%d')

    def clean_numero_documento(self):
        numero_documento = self.cleaned_data.get('numero_documento')
        if numero_documento:
            if not numero_documento.isdigit():
                raise ValidationError('El número de cédula solo debe contener dígitos.')
            if len(numero_documento) != 8:
                raise ValidationError('El número de cédula debe tener exactamente 8 dígitos.')
        return numero_documento

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if nombre:
            # Permite letras, espacios y apóstrofes/guiones (común en nombres/apellidos)
            if not all(c.isalpha() or c.isspace() or c in "-'" for c in nombre):
                 raise ValidationError('Los nombres solo deben contener letras, espacios, apóstrofes o guiones.')
            if len(nombre) > 30:
                raise ValidationError('El nombre no debe exceder los 30 caracteres.')
        return nombre

    def clean_apellido(self):
        apellido = self.cleaned_data.get('apellido')
        if apellido:
             # Permite letras, espacios y apóstrofes/guiones (común en nombres/apellidos)
            if not all(c.isalpha() or c.isspace() or c in "-'" for c in apellido):
                raise ValidationError('Los apellidos solo deben contener letras, espacios, apóstrofes o guiones.')
            if len(apellido) > 20:
                raise ValidationError('El apellido no debe exceder los 20 caracteres.')
        return apellido

    # Validación de confirmación de email (opcional pero buena práctica)
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        confirmar_email = cleaned_data.get("confirmar_email")

        # Solo valida si ambos emails fueron ingresados
        if email and confirmar_email and email != confirmar_email:
            self.add_error('confirmar_email', "Los correos electrónicos no coinciden.")

        return cleaned_data


class DireccionForm(forms.ModelForm):
    class Meta:
        model = Direccion
        fields = ['ciudad', 'direccion', 'codigo_postal']
        widgets = {
            # Mantenemos HiddenInput
            'ciudad': forms.HiddenInput(),
            'direccion': forms.TextInput(attrs={
                'class': 'form-control mb-2',
                'placeholder': 'Ej: Av. Principal, Calle 1, Casa 123'
            }),
            'codigo_postal': forms.TextInput(attrs={
                'class': 'form-control mb-2',
                'placeholder': 'Ej: 1010',
                'maxlength': '4'
            }),
        }
        labels = {
            'direccion': 'Dirección',
            'codigo_postal': 'Código Postal',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacemos ciudad NO requerido explícitamente en el formulario
        self.fields['ciudad'].required = False
        # Mantenemos el queryset por si acaso, aunque no se use en el render
        self.fields['ciudad'].queryset = Ciudad.objects.all()

    # Eliminamos las validaciones clean_ciudad y clean que dependían de la ciudad aquí


class TelefonoForm(forms.ModelForm):
    class Meta:
        model = Telefono
        fields = ['tipo_telefono', 'numero', 'es_principal']
        widgets = {
            'tipo_telefono': forms.Select(attrs={'class': 'form-control mb-2'}),
            'numero': forms.TextInput(attrs={
                'class': 'form-control mb-2',
                'placeholder': 'Ej: 04121234567',
                'maxlength': '11'
            }),
            'es_principal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'tipo_telefono': 'Tipo de Teléfono',
            'numero': 'Número',
            'es_principal': 'Teléfono Principal',
        }

    def clean_numero(self):
        numero = self.cleaned_data.get('numero')
        # La validación solo se aplica si se ingresa un número
        if numero:
            if len(numero) != 11:
                raise ValidationError('El número de teléfono debe tener exactamente 11 dígitos.')
            if not numero.isdigit():
                raise ValidationError('El número de teléfono solo debe contener dígitos.')
        # Si no se ingresa número y el campo no es obligatorio, se permite pasar
        return numero

# Formsets
DireccionFormSet = inlineformset_factory(
    Paciente, Direccion, form=DireccionForm,
    extra=1, can_delete=True,
    fields=['ciudad', 'direccion', 'codigo_postal']
)

TelefonoFormSet = inlineformset_factory(
    Paciente, Telefono, form=TelefonoForm,
    extra=1, can_delete=True,
    fields=['tipo_telefono', 'numero', 'es_principal']
)

class TipoTelefonoForm(forms.ModelForm):
    class Meta:
        model = TipoTelefono
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Móvil, Casa, Trabajo'}),
        }