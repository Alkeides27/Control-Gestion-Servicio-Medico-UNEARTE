from django import forms
from django.core.exceptions import ValidationError
from .models import HistorialMedico
from pacientes.models import Paciente
from inventario.models import Medicamento

class HistorialMedicoForm(forms.ModelForm):

    class Meta:
        model = HistorialMedico
        fields = [
            'paciente',
        ]
        widgets = {
            'paciente': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'paciente': 'Paciente',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

