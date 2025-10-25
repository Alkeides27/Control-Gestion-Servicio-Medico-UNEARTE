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
        
        # Poblar los querysets de los campos ManyToMany
        self.fields['alergias'].queryset = Alergia.objects.all()
        self.fields['enfermedades_preexistentes'].queryset = Enfermedad.objects.all()
        self.fields['medicamentos_actuales'].queryset = Medicamento.objects.all()
