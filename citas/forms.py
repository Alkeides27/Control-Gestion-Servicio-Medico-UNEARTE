from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Cita, EstadoCita, TipoCita, MotivoCita
from pacientes.models import Paciente

class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = [
            'paciente',
            'tipo_cita',
            'motivo',
            'fecha',
            'hora_inicio',
            'hora_fin',
            'estado',
            'observaciones',
        ]
        widgets = {
            'paciente': forms.Select(attrs={'class': 'form-control'}),
            'tipo_cita': forms.Select(attrs={'class': 'form-control'}),
            'motivo': forms.Select(attrs={'class': 'form-control'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'hora_inicio': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observaciones adicionales sobre la cita'}),
        }
        labels = {
            'paciente': 'Paciente',
            'tipo_cita': 'Tipo de Cita',
            'motivo': 'Motivo',
            'fecha': 'Fecha',
            'hora_inicio': 'Hora de Inicio',
            'hora_fin': 'Hora de Fin',
            'estado': 'Estado',
            'observaciones': 'Observaciones',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['paciente'].queryset = Paciente.objects.all()
        self.fields['tipo_cita'].queryset = TipoCita.objects.all()
        self.fields['motivo'].queryset = MotivoCita.objects.all()
        self.fields['estado'].queryset = EstadoCita.objects.all()
        
        # Establecer valores mínimos para fecha y hora SOLO para nuevas citas
        if not self.instance.pk:
            today = timezone.now().date()
            self.fields['fecha'].widget.attrs['min'] = today
        self.fields['hora_inicio'].widget.attrs['min'] = '00:00'
        self.fields['hora_fin'].widget.attrs['min'] = '00:00'

    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha')
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fin = cleaned_data.get('hora_fin')
        paciente = cleaned_data.get('paciente')

        # Validar que la hora de fin sea posterior a la hora de inicio
        if hora_inicio and hora_fin and hora_fin <= hora_inicio:
            raise ValidationError('La hora de fin debe ser posterior a la hora de inicio.')

        # Validar que no haya citas solapadas para el mismo paciente
        if fecha and hora_inicio and hora_fin and paciente:
            citas_solapadas = Cita.objects.filter(
                paciente=paciente,
                fecha=fecha,
                hora_inicio__lt=hora_fin,
                hora_fin__gt=hora_inicio
            )
            
            # Excluir la instancia actual si estamos editando
            if self.instance.pk:
                citas_solapadas = citas_solapadas.exclude(pk=self.instance.pk)
                
            if citas_solapadas.exists():
                raise ValidationError('El paciente ya tiene una cita programada en este horario.')

        # Validar que la fecha no sea en el pasado SOLO para nuevas citas
        if not self.instance.pk and fecha and fecha < timezone.now().date():
            raise ValidationError('No se pueden programar citas en fechas pasadas.')

        return cleaned_data

    def clean_fecha(self):
        fecha = self.cleaned_data.get('fecha')
        # Validar que la fecha no sea en el pasado SOLO para nuevas citas
        if not self.instance.pk and fecha and fecha < timezone.now().date():
            raise ValidationError('No se pueden programar citas en fechas pasadas.')
        return fecha

class EstadoCitaForm(forms.ModelForm):
    class Meta:
        model = EstadoCita
        fields = ['nombre', 'descripcion', 'color']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '#RRGGBB'}),
        }
        labels = {
            'nombre': 'Nombre',
            'descripcion': 'Descripción',
            'color': 'Color (Código HEX)',
        }

    def clean_color(self):
        color = self.cleaned_data.get('color')
        if color and not color.startswith('#'):
            raise ValidationError('El código de color debe comenzar con #.')
        if color and len(color) != 7:
            raise ValidationError('El código de color debe tener 7 caracteres.')
        return color

class TipoCitaForm(forms.ModelForm):
    class Meta:
        model = TipoCita
        fields = ['nombre', 'descripcion', 'duracion_estimada']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'duracion_estimada': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }
        labels = {
            'nombre': 'Nombre',
            'descripcion': 'Descripción',
            'duracion_estimada': 'Duración Estimada (minutos)',
        }

    def clean_duracion_estimada(self):
        duracion = self.cleaned_data.get('duracion_estimada')
        if duracion and duracion <= 0:
            raise ValidationError('La duración estimada debe ser mayor que cero.')
        return duracion

class MotivoCitaForm(forms.ModelForm):
    class Meta:
        model = MotivoCita
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'nombre': 'Nombre',
            'descripcion': 'Descripción',
        }