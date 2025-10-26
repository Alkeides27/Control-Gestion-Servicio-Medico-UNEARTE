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
                'maxlength': '11',
                'pattern': '[0-9]*'
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