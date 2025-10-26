# Al final de historiales/forms.py

from django import forms
from .models import (
    HistorialMedico, # El contenedor
    HistoriaGeneral,
    HistoriaNutricion,
    DocumentoJustificativo,
    DocumentoReferencia,
    DocumentoReposo,
    DocumentoRecipe
)
from crispy_forms.helper import FormHelper # Asumiendo que usas crispy_forms
from crispy_forms.layout import Layout, Fieldset, Row, Column, Submit


# Formulario para el Contenedor (HistorialMedico) - Lo simplificamos
class HistorialMedicoForm(forms.ModelForm):
    class Meta:
        model = HistorialMedico
        # Solo incluimos los campos del contenedor que se definen al crear
        fields = ['paciente'] # El médico se asigna automáticamente en la vista
        widgets = {
            'paciente': forms.HiddenInput() # Lo pasaremos por URL o contexto
        }

# Formulario para HistoriaGeneral
class HistoriaGeneralForm(forms.ModelForm):
    class Meta:
        model = HistoriaGeneral
        # Excluimos el padre porque se asigna automáticamente
        exclude = ['historial_padre']
        widgets = {
            # Usar Textarea con menos filas para ahorrar espacio
            'motivo_consulta': forms.Textarea(attrs={'rows': 3}),
            'enfermedad_actual': forms.Textarea(attrs={'rows': 4}),
            'examen_fisico': forms.Textarea(attrs={'rows': 4}),
            'diagnostico': forms.Textarea(attrs={'rows': 3}),
            'plan': forms.Textarea(attrs={'rows': 4}),
            'antecedentes_personales': forms.Textarea(attrs={'rows': 3}),
            'antecedentes_familiares': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('peso', css_class='form-group col-md-4 mb-0'),
                Column('talla', css_class='form-group col-md-4 mb-0'),
                Column('ta', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            'motivo_consulta',
            'enfermedad_actual',
            'antecedentes_personales',
            'antecedentes_familiares',
            'examen_fisico',
            'diagnostico',
            'plan',
        )
        # Quitamos la etiqueta del formulario para que no diga "Historia General"
        self.helper.form_tag = False


# Formulario para HistoriaNutricion (¡Es largo!)
class HistoriaNutricionForm(forms.ModelForm):
    class Meta:
        model = HistoriaNutricion
        exclude = ['historial_padre']
        # Definir widgets si es necesario para Textarea, Select, etc.
        widgets = {
            'medicamentos': forms.Textarea(attrs={'rows': 2}),
            'alergias_alimentarias': forms.Textarea(attrs={'rows': 2}),
            'intolerancias_alimentarias': forms.Textarea(attrs={'rows': 2}),
            'recordatorio_24h_d': forms.Textarea(attrs={'rows': 1}),
            'recordatorio_24h_m1': forms.Textarea(attrs={'rows': 1}),
            'recordatorio_24h_a': forms.Textarea(attrs={'rows': 1}),
            'recordatorio_24h_m2': forms.Textarea(attrs={'rows': 1}),
            'recordatorio_24h_c': forms.Textarea(attrs={'rows': 1}),
            'datos_laboratorio': forms.Textarea(attrs={'rows': 3}),
            'tabla_antropometrica': forms.Textarea(attrs={'rows': 5}),
            'dx_nutricional': forms.Textarea(attrs={'rows': 3}),
            'observaciones': forms.Textarea(attrs={'rows': 4}),
            'evolucion': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        # Organizar los campos usando Fieldsets y Rows/Columns de crispy-forms
        self.helper.layout = Layout(
            Fieldset(
                'Hábitos Psicobiológicos',
                Row(
                    Column('medicamentos', css_class='form-group col-md-6 mb-0'),
                    Column('cafeicos', css_class='form-group col-md-6 mb-0'),
                ),
                 Row(
                    Column('sueno', css_class='form-group col-md-4 mb-0'),
                    Column('cigarros', css_class='form-group col-md-4 mb-0'),
                     Column('apetito', css_class='form-group col-md-4 mb-0'),
                ),
                 Row(
                    Column('oh', css_class='form-group col-md-6 mb-0'),
                    Column('act_fisica', css_class='form-group col-md-6 mb-0'),
                ),
            ),
            Fieldset(
                'Hábitos Alimentarios',
                Row(
                    Column('n_comidas_dia', css_class='form-group col-md-4 mb-0'),
                    Column('n_meriendas_dia', css_class='form-group col-md-4 mb-0'),
                    Column('hidricos_vasos_dia', css_class='form-group col-md-4 mb-0'),
                ),
                'alergias_alimentarias',
                'intolerancias_alimentarias',
            ),
             Fieldset(
                'Examen Funcional',
                Row(
                    Column('funcional_masticacion', css_class='form-group col-md-2'),
                    Column('funcional_disfagia', css_class='form-group col-md-2'),
                    Column('funcional_nauseas', css_class='form-group col-md-2'),
                    Column('funcional_vomitos', css_class='form-group col-md-2'),
                    Column('funcional_pirosis', css_class='form-group col-md-2'),
                    Column('funcional_rge', css_class='form-group col-md-2'),
                ),
                Row(
                    Column('micciones', css_class='form-group col-md-4 mb-0'),
                    Column('periodos_menstruales', css_class='form-group col-md-4 mb-0'),
                    Column('evacuaciones', css_class='form-group col-md-4 mb-0'),
                ),
            ),
            Fieldset(
                'Frecuencia de Consumo',
                # Añadir aquí todas las filas y columnas para los campos 'frec_*'
                # Ejemplo para Lista 1:
                Row(
                    Column('frec_leche_comp', css_class='form-group col-md-3'),
                    Column('frec_leche_des', css_class='form-group col-md-3'),
                    Column('frec_yogurt_nat', css_class='form-group col-md-3'),
                    Column('frec_yogurt_des', css_class='form-group col-md-3'),
                ),
                # ... (Continuar para todas las listas)
            ),
            Fieldset(
                'Recordatorio 24h',
                'recordatorio_24h_d', 'recordatorio_24h_m1', 'recordatorio_24h_a',
                'recordatorio_24h_m2', 'recordatorio_24h_c',
            ),
            Fieldset(
                'Datos Antropométricos y de Laboratorio',
                'datos_laboratorio',
                Row(
                    Column('antropo_peso_usual', css_class='form-group col-md-3'),
                    Column('antropo_peso_max', css_class='form-group col-md-3'),
                    Column('antropo_peso_min', css_class='form-group col-md-3'),
                    Column('antropo_peso_rcom', css_class='form-group col-md-3'),
                ),
                 Row(
                    Column('antropo_peso_graso', css_class='form-group col-md-3'),
                    Column('antropo_peso_magro', css_class='form-group col-md-3'),
                    Column('antropo_porc_grasa', css_class='form-group col-md-3'),
                    Column('antropo_porc_grasa_rcom', css_class='form-group col-md-3'),
                ),
                'tabla_antropometrica',
            ),
             Fieldset(
                'Diagnóstico y Requerimiento Nutricional',
                'dx_nutricional',
                Row(
                    Column('req_rct', css_class='form-group col-md-4'),
                    Column('req_kcal_kg', css_class='form-group col-md-4'),
                ),
                Row(
                    Column('req_cho', css_class='form-group col-md-4'),
                     Column('req_prot', css_class='form-group col-md-4'),
                     Column('req_grasa', css_class='form-group col-md-4'),
                ),
            ),
            Fieldset(
                'Observaciones y Evolución',
                'observaciones',
                'evolucion',
            ),
        )
        self.helper.form_tag = False # Quitamos la etiqueta <form>


# --- Formularios para los Documentos ---

class DocumentoJustificativoForm(forms.ModelForm):
    class Meta:
        model = DocumentoJustificativo
        exclude = ['historial_padre']
        widgets = {
            'hora_entrada': forms.TimeInput(attrs={'type': 'time'}),
            'hora_salida': forms.TimeInput(attrs={'type': 'time'}),
        }
    # Puedes añadir un helper de Crispy si quieres estilizarlo

class DocumentoReferenciaForm(forms.ModelForm):
    class Meta:
        model = DocumentoReferencia
        exclude = ['historial_padre']
        widgets = {
            'motivo_referencia': forms.Textarea(attrs={'rows': 3}),
        }

class DocumentoReposoForm(forms.ModelForm):
    class Meta:
        model = DocumentoReposo
        exclude = ['historial_padre']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
            'debe_volver': forms.DateInput(attrs={'type': 'date'}),
        }

class DocumentoRecipeForm(forms.ModelForm):
    class Meta:
        model = DocumentoRecipe
        exclude = ['historial_padre']
        widgets = {
            'texto_recipe': forms.Textarea(attrs={'rows': 6}),
        }