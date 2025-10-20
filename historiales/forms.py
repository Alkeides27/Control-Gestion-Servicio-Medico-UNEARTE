from django import forms
from django.core.exceptions import ValidationError
from .models import HistorialMedico, Alergia, Enfermedad
from pacientes.models import Paciente
from inventario.models import Medicamento

class HistorialMedicoForm(forms.ModelForm):

    class Meta:
        model = HistorialMedico
        fields = [
            'paciente',
            'alergias',
            'enfermedades_preexistentes',
            'medicamentos_actuales',
        ]
        widgets = {
            'paciente': forms.Select(attrs={'class': 'form-control'}),
            'alergias': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            'enfermedades_preexistentes': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            'medicamentos_actuales': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'paciente': 'Paciente',
            'alergias': 'Alergias Conocidas',
            'enfermedades_preexistentes': 'Enfermedades Preexistentes',
            'medicamentos_actuales': 'Medicamentos Actuales',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar pacientes que no tienen historial en la creación
        if not self.instance.pk:
            self.fields['paciente'].queryset = Paciente.objects.filter(historial_medico__isnull=True)
        else:
            # En edición, el campo paciente no se puede cambiar
            self.fields['paciente'].disabled = True
            self.fields['paciente'].queryset = Paciente.objects.filter(pk=self.instance.paciente.pk)

        # Poblar los querysets de los campos ManyToMany
        self.fields['alergias'].queryset = Alergia.objects.all()
        self.fields['enfermedades_preexistentes'].queryset = Enfermedad.objects.all()
        self.fields['medicamentos_actuales'].queryset = Medicamento.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        
        # Validar que al menos un campo de historial tenga información
        if not cleaned_data.get('alergias') and not cleaned_data.get('enfermedades_preexistentes') and not cleaned_data.get('medicamentos_actuales'):
            raise ValidationError(
                'Debe registrar al menos una alergia, enfermedad o medicamento.',
                code='no_data'
            )
            
        return cleaned_data
        labels = {
            'paciente': 'Paciente',
            'alergias': 'Alergias Conocidas',
            'enfermedades_preexistentes': 'Enfermedades Preexistentes',
            'medicamentos_actuales': 'Medicamentos Actuales',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar pacientes que no tienen historial en la creación
        if not self.instance.pk:
            self.fields['paciente'].queryset = Paciente.objects.filter(historial_medico__isnull=True)
        else:
            # En edición, el campo paciente no se puede cambiar
            self.fields['paciente'].disabled = True
            self.fields['paciente'].queryset = Paciente.objects.filter(pk=self.instance.paciente.pk)

        # Poblar los querysets de los campos ManyToMany
        self.fields['alergias'].queryset = Alergia.objects.all()
        self.fields['enfermedades_preexistentes'].queryset = Enfermedad.objects.all()
        self.fields['medicamentos_actuales'].queryset = Medicamento.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        
        # Lógica para crear nuevas alergias/enfermedades "al vuelo"
        nueva_alergia_nombre = cleaned_data.get('nueva_alergia')
        if nueva_alergia_nombre:
            alergia, created = Alergia.objects.get_or_create(nombre=nueva_alergia_nombre.strip())
            # Añadir la nueva alergia a la selección
            cleaned_data['alergias'] = cleaned_data['alergias'].union(Alergia.objects.filter(pk=alergia.pk))

        nueva_enfermedad_nombre = cleaned_data.get('nueva_enfermedad')
        if nueva_enfermedad_nombre:
            enfermedad, created = Enfermedad.objects.get_or_create(nombre=nueva_enfermedad_nombre.strip())
            # Añadir la nueva enfermedad a la selección
            cleaned_data['enfermedades_preexistentes'] = cleaned_data['enfermedades_preexistentes'].union(Enfermedad.objects.filter(pk=enfermedad.pk))

        # Validar que al menos un campo de historial tenga información
        if not cleaned_data.get('alergias') and not cleaned_data.get('enfermedades_preexistentes') and not cleaned_data.get('medicamentos_actuales'):
            raise ValidationError(
                'Debe registrar al menos una alergia, enfermedad o medicamento.',
                code='no_data'
            )
            
        return cleaned_data
