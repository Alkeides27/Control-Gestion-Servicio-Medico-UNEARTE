from django import forms
from django.core.exceptions import ValidationError
from .models import (
    HistorialMedico,
    HistoriaGeneral,
    HistoriaNutricion,
    DocumentoJustificativo,
    DocumentoReferencia,
    DocumentoReposo,
    DocumentoRecipe
)
from pacientes.models import Paciente, Genero # Importar Paciente y Genero
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column, Submit, HTML, Div, Field
from crispy_forms.bootstrap import AppendedText, PrependedText

# --- Formulario Contenedor (Sin cambios) ---
class HistorialMedicoForm(forms.ModelForm):
    class Meta:
        model = HistorialMedico
        exclude = ['paciente', 'medico', 'fecha']

# --- Formulario Historia General (REVISADO para Pág. 9 y Creación de Paciente) ---
class HistoriaGeneralForm(forms.ModelForm):
    # --- CAMPOS PARA CREACIÓN DE PACIENTE (Solo si create_patient=True) ---
    # Usamos nombres distintos para evitar colisiones con los campos de visualización
    create_nombre = forms.CharField(label="Nombre del Paciente", required=False, max_length=100)
    create_apellido = forms.CharField(label="Apellido del Paciente", required=False, max_length=100)
    create_cedula = forms.CharField(label="Cédula", required=False, max_length=8) # Maxlength 8
    create_fecha_nacimiento = forms.DateField(label="Fecha de Nacimiento", required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    create_sexo = forms.ChoiceField(label="Sexo", choices=Genero.choices, required=False)
    create_telefono = forms.CharField(label="Teléfono", required=False, max_length=11) # Maxlength 11

    # --- CAMPOS PARA VISUALIZACIÓN DE PACIENTE (Solo si create_patient=False) ---
    display_nombre_paciente = forms.CharField(label="Nombre", required=False, disabled=True)
    display_cedula_paciente = forms.CharField(label="Cédula", required=False, disabled=True)
    display_edad_paciente = forms.CharField(label="Edad", required=False, disabled=True)
    display_sexo_paciente = forms.CharField(label="Sexo", required=False, disabled=True)
    display_telefono_paciente = forms.CharField(label="Telf.", required=False, disabled=True)
    display_fecha_nac_paciente = forms.CharField(label="Fecha de Nac.", required=False, disabled=True)
    medico_nombre = forms.CharField(label="Médico Tratante", required=False, disabled=True)

    class Meta:
        model = HistoriaGeneral
        exclude = ['historial_padre']
        widgets = {
            'tipo_afiliado': forms.RadioSelect(attrs={'class': 'form-check-inline'}),
            'antf_otros': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Especificar otros antecedentes familiares...'}),
            'antp_otros': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Especificar otros antecedentes personales...'}),
            'motivo_consulta': forms.Textarea(attrs={'rows': 3}),
            'hea': forms.Textarea(attrs={'rows': 4}),
            'examen_fisico': forms.Textarea(attrs={'rows': 5}),
            'diagnostico': forms.Textarea(attrs={'rows': 3}),
            'plan': forms.Textarea(attrs={'rows': 4}),
            'enfermero_nombre': forms.TextInput(),
        }
        labels = { 'hea': 'HEA (Historia Epidem. y Ambiental)', }

    def __init__(self, *args, **kwargs):
        # Sacamos los argumentos personalizados antes de llamar al super
        paciente = kwargs.pop('paciente', None)
        medico = kwargs.pop('medico', None)
        create_patient = kwargs.pop('create_patient', False) # Flag para saber si creamos paciente

        super().__init__(*args, **kwargs)

        if medico:
            self.fields['medico_nombre'].initial = medico.get_full_name()

        self.helper = FormHelper()
        self.helper.form_tag = False

        # --- Lógica Condicional para Campos y Layout ---
        if create_patient:
            # Hacemos requeridos los campos de creación de paciente
            self.fields['create_nombre'].required = True
            self.fields['create_apellido'].required = True
            self.fields['create_cedula'].required = True
            self.fields['create_fecha_nacimiento'].required = True
            self.fields['create_sexo'].required = True
            self.fields['create_telefono'].required = True
            
            # Ajustamos el widget de cédula para limitar longitud en HTML
            self.fields['create_cedula'].widget = forms.TextInput(attrs={'maxlength': '8'})


            # Layout para CREAR PACIENTE
            datos_personales_layout = Fieldset(
                'Datos del Nuevo Paciente',
                Row(
                    Column('create_nombre', css_class='col-md-6'),
                    Column('create_apellido', css_class='col-md-6'),
                ),
                Row(
                    Column('create_cedula', css_class='col-md-3'),
                    Column('create_fecha_nacimiento', css_class='col-md-3'),
                    Column('create_sexo', css_class='col-md-3'),
                    Column('create_telefono', css_class='col-md-3'),
                ),
                 Row( # Campos editables del historial
                    Column('peso', css_class='col-md-2 offset-md-6'), # Desplazados
                    Column('talla', css_class='col-md-2'),
                    Column('ta', css_class='col-md-2'),
                ),
                css_class='border rounded p-3 mb-3 bg-light' # Fondo ligero para indicar creación
            )
        else:
            # Llenamos los campos de visualización si hay paciente
            if paciente:
                self.fields['display_nombre_paciente'].initial = f"{paciente.nombre} {paciente.apellido}"
                self.fields['display_cedula_paciente'].initial = paciente.numero_documento
                self.fields['display_edad_paciente'].initial = paciente.edad
                self.fields['display_sexo_paciente'].initial = paciente.get_genero_display()
                telefono_principal = paciente.telefonos.filter(es_principal=True).first()
                self.fields['display_telefono_paciente'].initial = telefono_principal.numero if telefono_principal else 'N/A'
                self.fields['display_fecha_nac_paciente'].initial = paciente.fecha_nacimiento.strftime('%d/%m/%Y') if paciente.fecha_nacimiento else 'N/A'

            # Layout para VISUALIZAR PACIENTE (como antes)
            datos_personales_layout = Fieldset(
                'Datos Personales del Paciente',
                Row(
                    Column('display_nombre_paciente', css_class='col-md-6'),
                    Column('display_fecha_nac_paciente', css_class='col-md-3'),
                    Column('display_cedula_paciente', css_class='col-md-3'),
                ),
                Row(
                    Column('display_edad_paciente', css_class='col-md-2'),
                    Column('display_sexo_paciente', css_class='col-md-2'),
                    Column('display_telefono_paciente', css_class='col-md-3'),
                    Column('peso', css_class='col-md-2'),
                    Column('talla', css_class='col-md-1'),
                    Column('ta', css_class='col-md-2'),
                ),
                css_class='border rounded p-3 mb-3'
            )

        # --- Layout Común ---
        self.helper.layout = Layout(
            Row( Column('ceca', css_class='col-md-6'), Column(Field('tipo_afiliado', css_class='form-check-inline'), css_class='col-md-6 d-flex align-items-center flex-wrap'), css_class='mb-3' ),
            datos_personales_layout, # Layout condicional
            Fieldset(
                'Historia Médica',
                HTML('<h6 class="mt-2">Antecedentes Familiares</h6>'),
                Row( Column('antf_diabetes', css_class='col-auto form-check'), Column('antf_hepatitis', css_class='col-auto form-check'), Column('antf_cardiovascular', css_class='col-auto form-check'), Column('antf_respiratoria', css_class='col-auto form-check'), Column('antf_neurologica', css_class='col-auto form-check'), css_class='d-flex flex-wrap' ),
                'antf_otros',
                HTML('<h6 class="mt-3">Antecedentes Personales</h6>'),
                Row( Column('antp_diabetes', css_class='col-auto form-check'), Column('antp_hepatitis', css_class='col-auto form-check'), Column('antp_cardiovascular', css_class='col-auto form-check'), Column('antp_respiratoria', css_class='col-auto form-check'), Column('antp_neurologica', css_class='col-auto form-check'), Column('antp_cirugia', css_class='col-auto form-check'), Column('antp_alergias', css_class='col-auto form-check'), Column('antp_its', css_class='col-auto form-check'), Column('antp_osteomusculares', css_class='col-auto form-check'), Column('antp_habitos', css_class='col-auto form-check'), css_class='d-flex flex-wrap' ),
                'antp_otros',
                'motivo_consulta', 'hea', 'examen_fisico', 'diagnostico', 'plan',
                css_class='border rounded p-3 mb-3 mt-3'
            ),
            Row(
                 Column('medico_nombre', css_class='col-md-6'),
                 Column( 'enfermero_nombre', css_class='col-md-6' ),
                 css_class='mt-4'
            )
        )

    # Validación adicional para cédula (silenciosa en el frontend)
    def clean_create_cedula(self):
        cedula = self.cleaned_data.get('create_cedula')
        # Si estamos creando paciente y la cédula está presente
        if self.fields['create_cedula'].required and cedula:
             if not cedula.isdigit():
                 raise ValidationError("La cédula solo debe contener números.")
             if len(cedula) > 8:
                 # Silenciosamente trunca a 8 dígitos en lugar de lanzar error visible
                 return cedula[:8]
             # Podrías añadir validación de unicidad aquí si es necesario
             # if Paciente.objects.filter(cedula=cedula).exists():
             #     raise ValidationError("Ya existe un paciente con esta cédula.")
        return cedula

    def clean_create_telefono(self):
         telefono = self.cleaned_data.get('create_telefono')
         if self.fields['create_telefono'].required and telefono:
             if not telefono.isdigit():
                 raise ValidationError("El teléfono solo debe contener números.")
             if len(telefono) > 11:
                 return telefono[:11] # Truncar silenciosamente
         return telefono

# --- Formulario Historia Nutrición (REVISADO Layout basado en Págs. 1 y 3) ---
class HistoriaNutricionForm(forms.ModelForm):
    class Meta:
        model = HistoriaNutricion
        exclude = ['historial_padre']
        widgets = {
            'motivo_consulta_nutricion': forms.Textarea(attrs={'rows': 2}), # Más pequeño en Pág 1
            'antp_nutri_otros': forms.Textarea(attrs={'rows': 1}),
            'antf_nutri_otros': forms.Textarea(attrs={'rows': 1}),
            'hab_medicamentos': forms.Textarea(attrs={'rows': 1}),
            'alim_alergias': forms.Textarea(attrs={'rows': 1}),
            'alim_intolerancias': forms.Textarea(attrs={'rows': 1}),
            'recordatorio_24h_d': forms.Textarea(attrs={'rows': 1}),
            'recordatorio_24h_m1': forms.Textarea(attrs={'rows': 1}),
            'recordatorio_24h_a': forms.Textarea(attrs={'rows': 1}),
            'recordatorio_24h_m2': forms.Textarea(attrs={'rows': 1}),
            'recordatorio_24h_c': forms.Textarea(attrs={'rows': 1}),
            'datos_laboratorio': forms.Textarea(attrs={'rows': 3}),
            'tabla_antropometrica': forms.Textarea(attrs={'rows': 8}), # Más grande para tabla
            'dx_nutricional': forms.Textarea(attrs={'rows': 2}),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
            'evolucion': forms.Textarea(attrs={'rows': 3}),
            'otros_basicos': forms.Textarea(attrs={'rows': 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(

            # --- PÁGINA 1 ---
            Fieldset(
                'Información Adicional (Nutrición)', # Grupo superior Pág 1
                Row(
                    Column('numero_historia_clinica', css_class='col-md-4'),
                    # Fecha está en el historial padre
                    # Nombre, Edad, Fecha Nac, CI, Teléfono, Dirección están en Paciente
                    Column('estado_civil', css_class='col-md-2'),
                    Column('empleo', css_class='col-md-3'),
                    Column('es_docente', css_class='col-md-1 form-check'), # Checkbox más pequeño
                    Column('otros_basicos', css_class='col-md-2'),
                ),
                Row(
                    Column('ceca', css_class='col-md-4'),
                    Column('mencion', css_class='col-md-4'),
                    Column('semestre', css_class='col-md-4'),
                ),
                 css_class='border rounded p-3 mb-3'
            ),

            Field('motivo_consulta_nutricion', css_class='mb-3'),

            # Antecedentes Pág 1 (Layout similar a HistoriaGeneral pero con campos _nutri)
             Fieldset(
                'Antecedentes Médicos (Nutrición)',
                Row(
                    Column(
                        HTML('<h6>Personales</h6>'),
                        Row(
                            Column('antp_nutri_diabetes', css_class='col-6 col-sm-4 form-check'), Column('antp_nutri_hta', css_class='col-6 col-sm-4 form-check'), Column('antp_nutri_cardiopatias', css_class='col-6 col-sm-4 form-check'),
                            Column('antp_nutri_cancer', css_class='col-6 col-sm-4 form-check'), Column('antp_nutri_gastritis', css_class='col-6 col-sm-4 form-check'), Column('antp_nutri_hipertiroidismo', css_class='col-6 col-sm-4 form-check'),
                            Column('antp_nutri_hipotiroidismo', css_class='col-6 col-sm-4 form-check'),
                        ),
                        Field('antp_nutri_otros', placeholder="Especifique otros..."),
                        css_class='col-md-6 border-end'
                    ),
                    Column(
                         HTML('<h6>Familiares</h6>'),
                         Row(
                            Column('antf_nutri_diabetes', css_class='col-6 col-sm-4 form-check'), Column('antf_nutri_hta', css_class='col-6 col-sm-4 form-check'), Column('antf_nutri_cardiopatias', css_class='col-6 col-sm-4 form-check'),
                            Column('antf_nutri_cancer', css_class='col-6 col-sm-4 form-check'), Column('antf_nutri_gastritis', css_class='col-6 col-sm-4 form-check'), Column('antf_nutri_hipertiroidismo', css_class='col-6 col-sm-4 form-check'),
                            Column('antf_nutri_hipotiroidismo', css_class='col-6 col-sm-4 form-check'),
                         ),
                        Field('antf_nutri_otros', placeholder="Especifique otros..."),
                        css_class='col-md-6'
                    ),
                ),
                 css_class='border rounded p-3 mb-3'
            ),

            # Hábitos Psicobiológicos Pág 1 (Layout en 2 columnas principales)
             Fieldset(
                'Hábitos Psicobiológicos',
                 Row(
                     Column( # Columna Izquierda
                         'hab_medicamentos',
                         'hab_cafeicos',
                         'hab_sueno',
                         'hab_cigarros',
                         'hab_oh',
                         css_class='col-md-6 border-end'
                     ),
                      Column( # Columna Derecha
                         'hab_apetito',
                         'hab_act_fisica',
                         # Dejamos espacio vacío para equilibrar
                         HTML('&nbsp;'),
                          HTML('&nbsp;'),
                           HTML('&nbsp;'),
                         css_class='col-md-6'
                     )
                 ),
                 css_class='border rounded p-3 mb-3'
            ),

             # Hábitos Alimentarios Pág 1
             Fieldset(
                'Hábitos Alimentarios',
                 Row( # Fila superior
                     Column('alim_n_comidas_dia', css_class='col-md-4'),
                     Column('alim_n_meriendas_dia', css_class='col-md-4'),
                     Column('alim_hidricos_vasos_dia', css_class='col-md-4'),
                 ),
                 # Fila inferior (TextAreas)
                 Row(
                     Column('alim_alergias', css_class='col-md-6'),
                     Column('alim_intolerancias', css_class='col-md-6'),
                 ),
                 css_class='border rounded p-3 mb-3'
            ),

            # Examen Funcional Pág 1
            Fieldset(
                'Examen Funcional',
                Row( # Checkboxes agrupados como en el PDF
                    Column(HTML('<strong>Síntomas:</strong>'), css_class='col-12 mb-2'),
                    Column('func_masticacion', css_class='col-auto form-check'), Column('func_disfagia', css_class='col-auto form-check'), Column('func_nauseas', css_class='col-auto form-check'),
                    Column('func_vomitos', css_class='col-auto form-check'), Column('func_pirosis', css_class='col-auto form-check'), Column('func_rge', css_class='col-auto form-check'),
                    css_class='d-flex flex-wrap'
                ),
                Row( # Fila inferior
                    Column('func_micciones', css_class='col-md-4'),
                    Column('func_evacuaciones', css_class='col-md-4'),
                    Column('func_periodos_menstruales', css_class='col-md-4 form-check align-self-center'), # Checkbox al final
                ),
                 css_class='border rounded p-3 mb-3'
            ),

            # Frecuencia de Consumo Pág 1 (Más compacto)
             Fieldset(
                'Frecuencia de Consumo de Alimentos',
                 Row( # Lista 1 y 2
                    Column(HTML('<h6>Lácteos (L1)</h6>'), 'frec_leche_comp', 'frec_leche_des', 'frec_yogurt_nat', 'frec_yogurt_des', css_class='col-md-4 border-end'),
                    Column(HTML('<h6>Vegetales (L2)</h6>'), 'frec_vegetales_crudos', 'frec_vegetales_cocidos', 'frec_vegetales_licuados', css_class='col-md-4 border-end'),
                    Column(HTML('<h6>Frutas (L3)</h6>'), 'frec_frutas_enteras', 'frec_frutas_licuadas', css_class='col-md-4'),
                 ),
                 HTML('<hr>'),
                 Row( # Lista 4
                     Column(HTML('<h6>Carbohidratos (L4)</h6>'), css_class='col-12'),
                     Column('frec_arepa', css_class='col-6 col-sm-4 col-md-2'), Column('frec_pan_blanco', css_class='col-6 col-sm-4 col-md-2'), Column('frec_pan_integral', css_class='col-6 col-sm-4 col-md-2'),
                     Column('frec_pasta', css_class='col-6 col-sm-4 col-md-2'), Column('frec_arroz', css_class='col-6 col-sm-4 col-md-2'), Column('frec_casabe', css_class='col-6 col-sm-4 col-md-2'),
                     Column('frec_tuberculos', css_class='col-6 col-sm-4 col-md-2'), Column('frec_platano', css_class='col-6 col-sm-4 col-md-2'), Column('frec_granos', css_class='col-6 col-sm-4 col-md-2'),
                     Column('frec_galletas', css_class='col-6 col-sm-4 col-md-2'), Column('frec_dulces', css_class='col-6 col-sm-4 col-md-2'), Column('frec_salados', css_class='col-6 col-sm-4 col-md-2'),
                 ),
                 HTML('<hr>'),
                 Row( # Lista 5
                     Column(HTML('<h6>Proteínas (L5)</h6>'), css_class='col-12'),
                     Column('frec_pollo_c_piel', css_class='col-6 col-sm-4 col-md-2'), Column('frec_pollo_s_piel', css_class='col-6 col-sm-4 col-md-2'), Column('frec_pescado', css_class='col-6 col-sm-4 col-md-2'),
                     Column('frec_res', css_class='col-6 col-sm-4 col-md-2'), Column('frec_pavo', css_class='col-6 col-sm-4 col-md-2'), Column('frec_cerdo', css_class='col-6 col-sm-4 col-md-2'),
                     Column('frec_huevos', css_class='col-6 col-sm-4 col-md-2'), Column('frec_embutidos', css_class='col-6 col-sm-4 col-md-2'), Column('frec_visceras', css_class='col-6 col-sm-4 col-md-2'),
                     Column('frec_otros_lista5', css_class='col-6 col-sm-4 col-md-2'),
                 ),
                 HTML('<hr>'),
                 Row( # Lista 6 y Otros
                     Column(HTML('<h6>Grasas (L6)</h6>'), 'frec_aceite', 'frec_mayonesa', 'frec_mantequilla', 'frec_margarina', 'frec_frutos_secos', 'frec_frituras', css_class='col-md-5 border-end'),
                     Column(HTML('<h6>Otros</h6>'), 'frec_azucar', 'frec_dulces_otros', 'frec_refrescos', 'frec_malta', 'frec_te_frio', 'frec_jugos_envasados', css_class='col-md-3 border-end'),
                     Column(HTML('<h6>&nbsp;</h6>'), 'frec_sal', 'frec_enlatados', 'frec_cubitos', 'frec_otros_final', css_class='col-md-4'),
                 ),
                 css_class='border rounded p-3 mb-3'
            ),

            # Recordatorio 24h Pág 1
             Fieldset(
                'Recordatorio de 24 Horas',
                 Row(
                     Column('recordatorio_24h_d', css_class='col-md-4', placeholder="Desayuno..."),
                     Column('recordatorio_24h_m1', css_class='col-md-4', placeholder="Media Mañana..."),
                     Column('recordatorio_24h_a', css_class='col-md-4', placeholder="Almuerzo..."),
                 ),
                 Row(
                     Column('recordatorio_24h_m2', css_class='col-md-4 offset-md-4', placeholder="Media Tarde..."),
                     Column('recordatorio_24h_c', css_class='col-md-4', placeholder="Cena..."),
                 ),
                 css_class='border rounded p-3 mb-3'
            ),

            # --- PÁGINA 3 ---
             Fieldset(
                'Datos de Laboratorio (Pág. 3)',
                 'datos_laboratorio',
                 css_class='border rounded p-3 mb-3'
            ),

             Fieldset(
                'Datos Antropométricos (Pág. 3)',
                 Row( # Primera fila de datos
                     Column('antropo_peso_usual', css_class='col-sm-6 col-md-3'),
                     Column('antropo_peso_max', css_class='col-sm-6 col-md-3'),
                     Column('antropo_peso_min', css_class='col-sm-6 col-md-3'),
                      Column('antropo_peso_rcom', css_class='col-sm-6 col-md-3'),
                 ),
                 Row( # Segunda fila de datos
                     Column('antropo_peso_graso', css_class='col-sm-6 col-md-3'),
                      Column('antropo_peso_magro', css_class='col-sm-6 col-md-3'),
                     Column('antropo_porc_grasa', css_class='col-sm-6 col-md-3'),
                     Column('antropo_porc_grasa_rcom', css_class='col-sm-6 col-md-3'),
                 ),
                 'tabla_antropometrica', # Textarea para la tabla
                 css_class='border rounded p-3 mb-3'
            ),

             Fieldset(
                'Diagnóstico y Requerimiento Nutricional (Pág. 3)',
                 'dx_nutricional',
                 Row( # Fila superior requerimientos
                     Column('req_rct', css_class='col-md-6'), Column('req_kcal_kg', css_class='col-md-6')
                 ),
                 Row( # Fila inferior porcentajes
                     Column('req_cho_porc', css_class='col-md-4'), Column('req_prot_porc', css_class='col-md-4'), Column('req_grasa_porc', css_class='col-md-4')
                 ),
                 css_class='border rounded p-3 mb-3'
            ),

            Fieldset(
                'Observaciones y Evolución (Pág. 3)',
                Row(
                    Column('observaciones', css_class='col-md-6'),
                    Column('evolucion', css_class='col-md-6'),
                ),
                 css_class='border rounded p-3 mb-3'
            ),
        )


# --- Formularios para Documentos (Layouts Revisados) ---

class DocumentoJustificativoForm(forms.ModelForm):
     class Meta:
        model = DocumentoJustificativo
        exclude = ['historial_padre']
        widgets = {
            'hora_entrada': forms.TimeInput(attrs={'type': 'time', 'step': '900'}),
            'hora_salida': forms.TimeInput(attrs={'type': 'time', 'step': '900'}),
        }
     def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False # Quitar <form> tag si se usa en modal o dentro de otro form
        self.helper.layout = Layout(
            # Imitando Pág 4
            Field('motivo_consulta'),
             Row(
                 Column( PrependedText('hora_entrada', 'De:'), css_class='col-md-6'),
                 Column( PrependedText('hora_salida', 'A:'), css_class='col-md-6'),
                 css_class='mb-3'
             ),
             # Los datos del paciente (Nombre, CI) se añadirán en la plantilla PDF
        )

class DocumentoReferenciaForm(forms.ModelForm):
    class Meta:
        model = DocumentoReferencia
        exclude = ['historial_padre']
        widgets = {
            'motivo_referencia': forms.Textarea(attrs={'rows': 5}), # Más espacio para motivo
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            # Imitando Pág 5
            Field('referido_a'),
            Field('motivo_referencia')
             # Los datos del paciente (Nombre, CI) se añadirán en la plantilla PDF
        )

class DocumentoReposoForm(forms.ModelForm):
    class Meta:
        model = DocumentoReposo
        exclude = ['historial_padre']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
            'debe_volver': forms.DateInput(attrs={'type': 'date'}),
            'diagnostico': forms.Textarea(attrs={'rows': 3}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            # Imitando Pág 6
            Field('consulta'),
            Field('diagnostico'),
            Row(
                 Column( AppendedText('duracion_dias', 'Días'), css_class='col-md-4'),
                 Column( PrependedText('fecha_inicio', 'Del'), css_class='col-md-4'),
                 Column( PrependedText('fecha_fin', 'Al'), css_class='col-md-4'),
                 css_class='mb-3'
            ),
            Field('debe_volver')
             # Los datos del paciente (Nombre, CI) se añadirán en la plantilla PDF
        )

class DocumentoRecipeForm(forms.ModelForm):
    class Meta:
        model = DocumentoRecipe
        exclude = ['historial_padre']
        widgets = {
            'texto_recipe': forms.Textarea(attrs={'rows': 10}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            # Imitando Pág 8 (similar a Pág 7 Indicaciones)
            Field('texto_recipe')
            # Los datos del paciente (Nombre, CI, Edad) se añadirán en la plantilla PDF
        )