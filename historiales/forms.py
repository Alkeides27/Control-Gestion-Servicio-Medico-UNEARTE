from django import forms
from .models import (
    HistorialMedico,
    HistoriaGeneral,
    HistoriaNutricion,
    DocumentoJustificativo,
    DocumentoReferencia,
    DocumentoReposo,
    DocumentoRecipe
)
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column, Submit, HTML, Div, Field
from crispy_forms.bootstrap import AppendedText, PrependedText # Para campos solo lectura

# --- Formulario Contenedor (Sin cambios) ---
class HistorialMedicoForm(forms.ModelForm):
    class Meta:
        model = HistorialMedico
        fields = ['paciente']
        widgets = {
            'paciente': forms.HiddenInput()
        }

# --- Formulario Historia General (REVISADO para Pág. 9 y extras) ---
class HistoriaGeneralForm(forms.ModelForm):
    # Campos adicionales para mostrar datos del paciente (no se guardan en este modelo)
    nombre_paciente = forms.CharField(label="Nombre", required=False, disabled=True)
    cedula_paciente = forms.CharField(label="Cédula", required=False, disabled=True)
    edad_paciente = forms.CharField(label="Edad", required=False, disabled=True)
    sexo_paciente = forms.CharField(label="Sexo", required=False, disabled=True)
    telefono_paciente = forms.CharField(label="Telf.", required=False, disabled=True)
    fecha_nac_paciente = forms.CharField(label="Fecha de Nac.", required=False, disabled=True)

    class Meta:
        model = HistoriaGeneral
        exclude = ['historial_padre']
        widgets = {
            # Checkboxes para tipo_afiliado (RadioSelect es mejor visualmente)
            'tipo_afiliado': forms.RadioSelect(attrs={'class': 'form-check-inline'}),
            # Checkboxes para Antecedentes (se renderizarán individualmente en el layout)
            'antf_otros': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Especificar otros antecedentes familiares...'}),
            'antp_otros': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Especificar otros antecedentes personales...'}),
            'motivo_consulta': forms.Textarea(attrs={'rows': 3}),
            'hea': forms.Textarea(attrs={'rows': 4}),
            'examen_fisico': forms.Textarea(attrs={'rows': 5}),
            'diagnostico': forms.Textarea(attrs={'rows': 3}),
            'plan': forms.Textarea(attrs={'rows': 4}),
            'enfermero_nombre': forms.TextInput(),
        }
        # Especificar labels si difieren del verbose_name del modelo
        labels = {
            'hea': 'HEA (Historia Epidem. y Ambiental)',
        }

    def __init__(self, *args, **kwargs):
        # Sacamos el paciente y el médico del kwargs si existen (pasados desde la vista)
        paciente = kwargs.pop('paciente', None)
        medico = kwargs.pop('medico', None)
        
        super().__init__(*args, **kwargs)
        
        # Llenar los campos de paciente si el objeto paciente fue pasado
        if paciente:
            self.fields['nombre_paciente'].initial = f"{paciente.nombre} {paciente.apellido}"
            self.fields['cedula_paciente'].initial = paciente.numero_documento
            self.fields['edad_paciente'].initial = paciente.edad
            self.fields['sexo_paciente'].initial = paciente.get_genero_display()
            telefono_principal = paciente.telefonos.filter(es_principal=True).first()
            self.fields['telefono_paciente'].initial = telefono_principal.numero if telefono_principal else 'N/A'
            self.fields['fecha_nac_paciente'].initial = paciente.fecha_nacimiento.strftime('%d/%m/%Y') if paciente.fecha_nacimiento else 'N/A'

        # --- Definición del Layout para imitar Pág. 9 ---
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            # Sección Superior: CECA y Tipo Afiliado
            Row(
                Column('ceca', css_class='col-md-6'),
                # Usamos Field directamente para RadioSelect inline
                Column(Field('tipo_afiliado', css_class='form-check-inline'), css_class='col-md-6 d-flex align-items-center flex-wrap'),
                css_class='mb-3'
            ),
            
            # Sección Datos Personales (Solo Visualización + Campos Editables)
            Fieldset(
                'Datos Personales',
                Row(
                    Column('nombre_paciente', css_class='col-md-6'),
                    Column('fecha_nac_paciente', css_class='col-md-3'),
                    Column('cedula_paciente', css_class='col-md-3'),
                ),
                Row(
                    Column('edad_paciente', css_class='col-md-2'),
                    Column('sexo_paciente', css_class='col-md-2'),
                    Column('telefono_paciente', css_class='col-md-3'),
                    # Campos editables de esta sección
                    Column('peso', css_class='col-md-2'),
                    Column('talla', css_class='col-md-1'), # Más pequeño
                    Column('ta', css_class='col-md-2'),
                ),
                css_class='border rounded p-3 mb-3'
            ),

            # Sección Historia Médica
            Fieldset(
                'Historia Médica',
                # Antecedentes con Checkboxes + Otros
                HTML('<h6 class="mt-2">Antecedentes Familiares</h6>'),
                Row( # Checkboxes inline
                    Column('antf_diabetes', css_class='col-auto form-check'),
                    Column('antf_hepatitis', css_class='col-auto form-check'),
                    Column('antf_cardiovascular', css_class='col-auto form-check'),
                    Column('antf_respiratoria', css_class='col-auto form-check'),
                    Column('antf_neurologica', css_class='col-auto form-check'),
                    css_class='d-flex flex-wrap' # Para que se ajusten
                ),
                'antf_otros',
                
                HTML('<h6 class="mt-3">Antecedentes Personales</h6>'),
                 Row(
                    Column('antp_diabetes', css_class='col-auto form-check'),
                    Column('antp_hepatitis', css_class='col-auto form-check'),
                    Column('antp_cardiovascular', css_class='col-auto form-check'),
                    Column('antp_respiratoria', css_class='col-auto form-check'),
                    Column('antp_neurologica', css_class='col-auto form-check'),
                    Column('antp_cirugia', css_class='col-auto form-check'),
                    Column('antp_alergias', css_class='col-auto form-check'),
                    Column('antp_its', css_class='col-auto form-check'),
                    Column('antp_osteomusculares', css_class='col-auto form-check'),
                    Column('antp_habitos', css_class='col-auto form-check'),
                    css_class='d-flex flex-wrap'
                ),
                'antp_otros',

                # Resto de campos
                'motivo_consulta',
                'hea',
                'examen_fisico',
                'diagnostico',
                'plan',
                css_class='border rounded p-3 mb-3 mt-3'
            ),

            # Sección Firmas (Médico no editable, Enfermero sí)
            Row(
                 Column(
                     PrependedText('', medico.get_full_name() if medico else 'N/A', css_class="disabled", wrapper_class="mb-0"),
                     HTML('<small class="form-text text-muted">Médico Tratante</small>'),
                     css_class='col-md-6'
                 ),
                 Column(
                     'enfermero_nombre', # Este sí es editable
                     css_class='col-md-6'
                 ),
                 css_class='mt-4'
            )
        )


# --- Formulario Historia Nutrición (ACTUALIZAR para reflejar cambios en modelo si los hubo) ---
class HistoriaNutricionForm(forms.ModelForm):
    # (Asegúrate de que este formulario refleje el modelo HistoriaNutricion de la respuesta anterior)
    # ... (El layout que te di antes debería servir, pero verifica los nombres de campo) ...
    class Meta:
        model = HistoriaNutricion
        exclude = ['historial_padre']
        # Añadir widgets para los nuevos BooleanFields si es necesario
        widgets = {
            'motivo_consulta_nutricion': forms.Textarea(attrs={'rows': 3}),
            'antp_nutri_otros': forms.Textarea(attrs={'rows': 2}),
            'antf_nutri_otros': forms.Textarea(attrs={'rows': 2}),
            'hab_medicamentos': forms.Textarea(attrs={'rows': 2}),
            'alim_alergias': forms.Textarea(attrs={'rows': 2}),
            'alim_intolerancias': forms.Textarea(attrs={'rows': 2}),
            'recordatorio_24h_d': forms.Textarea(attrs={'rows': 2}),
            'recordatorio_24h_m1': forms.Textarea(attrs={'rows': 1}),
            'recordatorio_24h_a': forms.Textarea(attrs={'rows': 2}),
            'recordatorio_24h_m2': forms.Textarea(attrs={'rows': 1}),
            'recordatorio_24h_c': forms.Textarea(attrs={'rows': 2}),
            'datos_laboratorio': forms.Textarea(attrs={'rows': 4}),
            'tabla_antropometrica': forms.Textarea(attrs={'rows': 6}),
            'dx_nutricional': forms.Textarea(attrs={'rows': 3}),
            'observaciones': forms.Textarea(attrs={'rows': 4}),
            'evolucion': forms.Textarea(attrs={'rows': 4}),
            'otros_basicos': forms.Textarea(attrs={'rows': 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        # (Aquí va el layout detallado de HistoriaNutricion que te pasé antes,
        # asegurándote de usar los nombres de campo correctos del modelo final)
        # Por brevedad, no lo repito aquí, pero usa el layout anterior.


# --- Formularios para Documentos (Sin cambios) ---
# ... (Mantener las clases DocumentoJustificativoForm, DocumentoReferenciaForm, etc. como estaban) ...
class DocumentoJustificativoForm(forms.ModelForm):
     class Meta: model = DocumentoJustificativo; exclude = ['historial_padre']
     widgets = {'hora_entrada': forms.TimeInput(attrs={'type': 'time', 'step': '900'}), 'hora_salida': forms.TimeInput(attrs={'type': 'time', 'step': '900'}),}
     def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs); self.helper = FormHelper();
        self.helper.layout = Layout('motivo_consulta', Row(Column('hora_entrada', css_class='col-md-6'), Column('hora_salida', css_class='col-md-6'),))

class DocumentoReferenciaForm(forms.ModelForm):
    class Meta: model = DocumentoReferencia; exclude = ['historial_padre']
    widgets = {'motivo_referencia': forms.Textarea(attrs={'rows': 4}),}
    def __init__(self, *args, **kwargs): super().__init__(*args, **kwargs); self.helper = FormHelper()

class DocumentoReposoForm(forms.ModelForm):
    class Meta: model = DocumentoReposo; exclude = ['historial_padre']
    widgets = {'fecha_inicio': forms.DateInput(attrs={'type': 'date'}), 'fecha_fin': forms.DateInput(attrs={'type': 'date'}), 'debe_volver': forms.DateInput(attrs={'type': 'date'}), 'diagnostico': forms.Textarea(attrs={'rows': 3}),}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs); self.helper = FormHelper()
        self.helper.layout = Layout('consulta', 'diagnostico', Row(Column('duracion_dias', css_class='col-md-4'), Column('fecha_inicio', css_class='col-md-4'), Column('fecha_fin', css_class='col-md-4'),), 'debe_volver')

class DocumentoRecipeForm(forms.ModelForm):
    class Meta: model = DocumentoRecipe; exclude = ['historial_padre']
    widgets = {'texto_recipe': forms.Textarea(attrs={'rows': 10}),}
    def __init__(self, *args, **kwargs): super().__init__(*args, **kwargs); self.helper = FormHelper()