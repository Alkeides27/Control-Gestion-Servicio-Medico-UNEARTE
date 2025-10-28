from django.db import models
from django.contrib.auth.models import User
from pacientes.models import Paciente
from django.utils import timezone

# -----------------------------------------------------------------------------
# MODELOS REVISADOS (26/10/2025) - ENFOQUE PÁGINA 9 PARA HistoriaGeneral
# -----------------------------------------------------------------------------

# 1. EL CONTENEDOR PRINCIPAL (Sesión Clínica) - Sin cambios
class HistorialMedico(models.Model):
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        verbose_name="Paciente"
    )
    medico = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Médico Tratante"
    )
    fecha = models.DateTimeField(
        default=timezone.now,
        verbose_name="Fecha de Consulta"
    )

    class Meta:
        verbose_name = "Historial (Contenedor)"
        verbose_name_plural = "Historiales (Contenedores)"
        ordering = ['-fecha']

    def __str__(self):
        return f"Historial de {self.paciente} - {self.fecha.strftime('%d/%m/%Y')}"


# -----------------------------------------------------------------------------
# 2. LOS FORMATOS (Datos de la consulta)
# -----------------------------------------------------------------------------

# --- MODELO PARA HISTORIA GENERAL (ESTRICTAMENTE PÁGINA 9 del TXT) ---
class HistoriaGeneral(models.Model):
    # Concatenación
    historial_padre = models.OneToOneField(
        HistorialMedico,
        on_delete=models.CASCADE,
        related_name="historia_general",
        verbose_name="Historial Padre"
    )
    
    # --- Campos Pág. 9: Sección Superior ---
    # Caracas, Fecha: Se obtienen de otro lugar (settings y historial_padre.fecha)
    # CECA: No se define en el TXT qué es, lo dejamos como texto por ahora.
    ceca = models.CharField(max_length=100, verbose_name="C.E.C.A.", null=True, blank=True) # Campo 3 Pág 9
    
    # Tipo de Afiliado (Checkboxes) - Campo 4 Pág 9
    TIPO_AFILIADO_CHOICES = [
        ('ADM', 'Administrativo'),
        ('OBR', 'Obrero'),
        ('DOC', 'Docente'),
        ('EST', 'Estudiante'),
        ('FAM', 'Familiar'),
    ]
    tipo_afiliado = models.CharField(
        max_length=3,
        choices=TIPO_AFILIADO_CHOICES,
        verbose_name="Tipo de Afiliado",
        null=True, blank=True
    )

    # --- Campos Pág. 9: Sección Datos Personales ---
    # Nombre, Fecha Nac, Cedula, Edad, Sexo, Telf: Ya están en el modelo Paciente.
    # Los mostraremos en el formulario pero no se guardan aquí.
    peso = models.FloatField(verbose_name="Peso (kg)", null=True, blank=True) # Campo 11 Pág 9
    talla = models.FloatField(verbose_name="Talla (cm)", null=True, blank=True) # Campo 12 Pág 9
    ta = models.CharField(max_length=50, verbose_name="Tensión Arterial (TA)", null=True, blank=True) # Campo 13 Pág 9

    # --- Campos Pág. 9: Historia Médica ---
    # Antecedentes: Usamos BooleanFields basados en Pág 2 (más específico) + Otros
    # Antecedentes Familiares (Campo 15 Pág 9)
    antf_diabetes = models.BooleanField(verbose_name="Diabetes (Fam.)", default=False)
    antf_hepatitis = models.BooleanField(verbose_name="Hepatitis (Fam.)", default=False)
    antf_cardiovascular = models.BooleanField(verbose_name="Cardiovascular (Fam.)", default=False)
    antf_respiratoria = models.BooleanField(verbose_name="Respiratoria (Fam.)", default=False)
    antf_neurologica = models.BooleanField(verbose_name="Neurológica (Fam.)", default=False)
    antf_otros = models.TextField(verbose_name="Otros Antecedentes Familiares", null=True, blank=True)

    # Antecedentes Personales (Campo 15 Pág 9)
    antp_diabetes = models.BooleanField(verbose_name="Diabetes (Pers.)", default=False)
    antp_hepatitis = models.BooleanField(verbose_name="Hepatitis (Pers.)", default=False)
    antp_cardiovascular = models.BooleanField(verbose_name="Cardiovascular (Pers.)", default=False)
    antp_respiratoria = models.BooleanField(verbose_name="Respiratoria (Pers.)", default=False)
    antp_neurologica = models.BooleanField(verbose_name="Neurológica (Pers.)", default=False)
    antp_cirugia = models.BooleanField(verbose_name="Cirugía (Pers.)", default=False)
    antp_alergias = models.BooleanField(verbose_name="Alergias (Pers.)", default=False)
    antp_its = models.BooleanField(verbose_name="ITS (Pers.)", default=False) # Enfermedades TS
    antp_osteomusculares = models.BooleanField(verbose_name="Osteomusculares (Pers.)", default=False)
    antp_habitos = models.BooleanField(verbose_name="Hábitos (Pers.)", default=False) # (Alcohol, drogas, etc.)
    antp_otros = models.TextField(verbose_name="Otros Antecedentes Personales", null=True, blank=True)

    # Motivo Consulta y HEA (Campo 16 y 17 Pág 9)
    # Nota: HEA en Pág 9 dice "Historia Epidemiológica y Ambiental"
    motivo_consulta = models.TextField(verbose_name="Motivo de Consulta", null=True, blank=True)
    hea = models.TextField(verbose_name="Historia Epidemiológica y Ambiental (HEA)", null=True, blank=True)

    # EXFIS, IDX, PLAN (Campos 18, 19, 20 Pág 9)
    examen_fisico = models.TextField(verbose_name="Examen Físico (EXFIS)", null=True, blank=True)
    diagnostico = models.TextField(verbose_name="Impresión Diagnóstica (IDX)", null=True, blank=True)
    plan = models.TextField(verbose_name="Plan y Tratamiento", null=True, blank=True)

    # --- Campos Pág. 9: Firma Profesional ---
    # Medico: Se obtiene del historial_padre.medico
    # Enfermero (Campo 22 Pág 9)
    enfermero_nombre = models.CharField(max_length=150, verbose_name="Enfermero/a", null=True, blank=True)

    class Meta:
        verbose_name = "Formato: Historia General (Pág. 9)"
        verbose_name_plural = "Formatos: Historias Generales (Pág. 9)"

    def __str__(self):
        return f"H. General (Pág. 9) de: {self.historial_padre.paciente}"


# --- MODELO PARA HISTORIA DE NUTRICIÓN (Págs. 1 y 3 del TXT) ---
# Mantenemos este modelo como lo definimos en la respuesta anterior (basado en Pág 1 y 3)
class HistoriaNutricion(models.Model):
    # Concatenación
    historial_padre = models.OneToOneField(
        HistorialMedico,
        on_delete=models.CASCADE,
        related_name="historia_nutricion",
        verbose_name="Historial Padre"
    )

    # --- Campos Pág. 1: Información Básica Adicional ---
    numero_historia_clinica = models.CharField(max_length=50, verbose_name="N° Historia Clínica", null=True, blank=True)
    estado_civil = models.CharField(max_length=50, verbose_name="Est. (Estado Civil)", null=True, blank=True)
    empleo = models.CharField(max_length=100, verbose_name="Empleo", null=True, blank=True)
    es_docente = models.BooleanField(verbose_name="Docente", default=False)
    otros_basicos = models.TextField(verbose_name="Otros (Datos Básicos)", null=True, blank=True)
    ceca = models.CharField(max_length=100, verbose_name="C.E.C.A. (Nutrición)", null=True, blank=True) # Campo diferente al de Pág 9
    mencion = models.CharField(max_length=100, verbose_name="Mención (Nutrición)", null=True, blank=True)
    semestre = models.CharField(max_length=50, verbose_name="Semestre (Nutrición)", null=True, blank=True)

    # --- Campos Pág. 1: Motivo de Consulta ---
    motivo_consulta_nutricion = models.TextField(verbose_name="Motivo de consulta (Nutrición)", null=True, blank=True)

    # --- Campos Pág. 1: Antecedentes Médicos (Nutrición) ---
    antp_nutri_diabetes = models.BooleanField(verbose_name="Diabetes (Pers.)", default=False)
    antp_nutri_hta = models.BooleanField(verbose_name="HTA (Pers.)", default=False)
    antp_nutri_cardiopatias = models.BooleanField(verbose_name="Cardiopatías (Pers.)", default=False)
    antp_nutri_cancer = models.BooleanField(verbose_name="Cáncer (Pers.)", default=False)
    antp_nutri_gastritis = models.BooleanField(verbose_name="Gastritis (Pers.)", default=False)
    antp_nutri_hipertiroidismo = models.BooleanField(verbose_name="Hipertiroidismo (Pers.)", default=False)
    antp_nutri_hipotiroidismo = models.BooleanField(verbose_name="Hipotiroidismo (Pers.)", default=False)
    antp_nutri_otros = models.TextField(verbose_name="Otros Antecedentes Personales (Nutri)", null=True, blank=True)

    antf_nutri_diabetes = models.BooleanField(verbose_name="Diabetes (Fam.)", default=False)
    antf_nutri_hta = models.BooleanField(verbose_name="HTA (Fam.)", default=False)
    antf_nutri_cardiopatias = models.BooleanField(verbose_name="Cardiopatías (Fam.)", default=False)
    antf_nutri_cancer = models.BooleanField(verbose_name="Cáncer (Fam.)", default=False)
    antf_nutri_gastritis = models.BooleanField(verbose_name="Gastritis (Fam.)", default=False)
    antf_nutri_hipertiroidismo = models.BooleanField(verbose_name="Hipertiroidismo (Fam.)", default=False)
    antf_nutri_hipotiroidismo = models.BooleanField(verbose_name="Hipotiroidismo (Fam.)", default=False)
    antf_nutri_otros = models.TextField(verbose_name="Otros Antecedentes Familiares (Nutri)", null=True, blank=True)

    # --- Campos Pág. 1: Hábitos y Estilo de Vida (Nutrición) ---
    hab_cafeicos = models.CharField(max_length=255, verbose_name="Café/Colas", null=True, blank=True)
    hab_cigarros = models.CharField(max_length=255, verbose_name="Cigarros", null=True, blank=True)
    hab_oh = models.CharField(max_length=255, verbose_name="OH (Alcohol)", null=True, blank=True)
    hab_medicamentos = models.TextField(verbose_name="Medicamentos", null=True, blank=True)
    hab_sueno = models.CharField(max_length=255, verbose_name="Sueño", null=True, blank=True)
    hab_apetito = models.CharField(max_length=255, verbose_name="Apetito", null=True, blank=True)
    hab_act_fisica = models.CharField(max_length=255, verbose_name="Actividad Física", null=True, blank=True)

    alim_n_comidas_dia = models.IntegerField(verbose_name="Nº Comidas/día", null=True, blank=True)
    alim_n_meriendas_dia = models.IntegerField(verbose_name="Nº Meriendas/día", null=True, blank=True)
    alim_hidricos_vasos_dia = models.IntegerField(verbose_name="Hidratación: Vasos/día", null=True, blank=True)
    alim_alergias = models.TextField(verbose_name="Alergias Alimentarias", null=True, blank=True)
    alim_intolerancias = models.TextField(verbose_name="Intolerancias Alimentarias", null=True, blank=True)

    # --- Campos Pág. 1: Examen Funcional (Nutrición) ---
    func_masticacion = models.BooleanField(verbose_name="Masticación Dificultosa", default=False)
    func_disfagia = models.BooleanField(verbose_name="Disfagia", default=False)
    func_nauseas = models.BooleanField(verbose_name="Náuseas", default=False)
    func_vomitos = models.BooleanField(verbose_name="Vómitos", default=False)
    func_pirosis = models.BooleanField(verbose_name="Pirosis", default=False)
    func_rge = models.BooleanField(verbose_name="RGE", default=False)
    func_periodos_menstruales = models.BooleanField(verbose_name="Síntomas Períodos Menstruales", default=False)
    func_micciones = models.CharField(max_length=255, verbose_name="Micciones", null=True, blank=True)
    func_evacuaciones = models.CharField(max_length=255, verbose_name="Evacuaciones", null=True, blank=True)

    # --- Campos Pág. 1: Frecuencia de Consumo de Alimentos (Nutrición) ---
    FREC_CHOICES = [
        ('', '---------'), ('D', 'Diario'), ('S', 'Semanal'), ('M', 'Mensual'), ('O', 'Ocasional'), ('N', 'Nunca'),
    ]
    frec_leche_comp = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Leche Comp.", null=True, blank=True)
    frec_leche_des = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Leche Des.", null=True, blank=True)
    frec_yogurt_nat = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Yogurt Nat.", null=True, blank=True)
    frec_yogurt_des = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Yogurt Des.", null=True, blank=True)
    frec_vegetales_crudos = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Vegetales Crudos", null=True, blank=True)
    frec_vegetales_cocidos = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Vegetales Cocidos", null=True, blank=True)
    frec_vegetales_licuados = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Vegetales Licuados", null=True, blank=True)
    frec_frutas_enteras = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Frutas Enteras", null=True, blank=True)
    frec_frutas_licuadas = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Frutas Licuadas", null=True, blank=True)
    frec_arepa = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Arepa", null=True, blank=True)
    frec_pan_blanco = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Pan Blanco", null=True, blank=True)
    frec_pan_integral = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Pan Integral", null=True, blank=True)
    frec_pasta = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Pasta", null=True, blank=True)
    frec_arroz = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Arroz", null=True, blank=True)
    frec_casabe = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Casabe", null=True, blank=True)
    frec_tuberculos = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Tubérculos", null=True, blank=True)
    frec_platano = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Plátano", null=True, blank=True)
    frec_granos = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Granos", null=True, blank=True)
    frec_galletas = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Galletas", null=True, blank=True)
    frec_dulces = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Dulces", null=True, blank=True)
    frec_salados = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Salados (Snacks)", null=True, blank=True)
    frec_pollo_c_piel = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Pollo c/piel", null=True, blank=True)
    frec_pollo_s_piel = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Pollo s/piel", null=True, blank=True)
    frec_pescado = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Pescado", null=True, blank=True)
    frec_res = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Res", null=True, blank=True)
    frec_pavo = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Pavo", null=True, blank=True)
    frec_cerdo = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Cerdo", null=True, blank=True)
    frec_huevos = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Huevos", null=True, blank=True)
    frec_embutidos = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Embutidos", null=True, blank=True)
    frec_visceras = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Vísceras", null=True, blank=True)
    frec_otros_lista5 = models.CharField(max_length=100, verbose_name="Otros (Lista 5)", null=True, blank=True)
    frec_aceite = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Aceite", null=True, blank=True)
    frec_mayonesa = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Mayonesa", null=True, blank=True)
    frec_mantequilla = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Mantequilla", null=True, blank=True)
    frec_margarina = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Margarina", null=True, blank=True)
    frec_frutos_secos = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Frutos Secos", null=True, blank=True)
    frec_frituras = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Frituras", null=True, blank=True)
    frec_azucar = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Azúcar", null=True, blank=True)
    frec_dulces_otros = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Dulces (Otros)", null=True, blank=True)
    frec_refrescos = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Refrescos", null=True, blank=True)
    frec_malta = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Malta", null=True, blank=True)
    frec_te_frio = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Té frío", null=True, blank=True)
    frec_jugos_envasados = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Jugos Envasados", null=True, blank=True)
    frec_sal = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Sal", null=True, blank=True)
    frec_enlatados = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Enlatados", null=True, blank=True)
    frec_cubitos = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Cubitos", null=True, blank=True)
    frec_otros_final = models.CharField(max_length=100, verbose_name="Otros (Final)", null=True, blank=True)

    # --- Campos Pág. 1: Recordatorio 24h (Nutrición) ---
    recordatorio_24h_d = models.TextField(verbose_name="Recordatorio 24h (Desayuno)", null=True, blank=True)
    recordatorio_24h_m1 = models.TextField(verbose_name="Recordatorio 24h (Media Mañana)", null=True, blank=True)
    recordatorio_24h_a = models.TextField(verbose_name="Recordatorio 24h (Almuerzo)", null=True, blank=True)
    recordatorio_24h_m2 = models.TextField(verbose_name="Recordatorio 24h (Media Tarde)", null=True, blank=True)
    recordatorio_24h_c = models.TextField(verbose_name="Recordatorio 24h (Cena)", null=True, blank=True)

    # --- Campos Pág. 3 (Nutrición) ---
    datos_laboratorio = models.TextField(verbose_name="Datos Laboratorio", null=True, blank=True)
    antropo_peso_usual = models.FloatField(verbose_name="Peso Usual (kg)", null=True, blank=True)
    antropo_peso_graso = models.FloatField(verbose_name="Peso Graso (kg)", null=True, blank=True)
    antropo_peso_max = models.FloatField(verbose_name="Peso Máx (kg)", null=True, blank=True)
    antropo_peso_magro = models.FloatField(verbose_name="Peso Magro (kg)", null=True, blank=True)
    antropo_peso_min = models.FloatField(verbose_name="Peso Mín (kg)", null=True, blank=True)
    antropo_porc_grasa = models.FloatField(verbose_name="% Grasa", null=True, blank=True)
    antropo_porc_grasa_rcom = models.FloatField(verbose_name="% Grasa Recomendado", null=True, blank=True)
    antropo_peso_rcom = models.FloatField(verbose_name="Peso Recomendado (kg)", null=True, blank=True)
    tabla_antropometrica = models.TextField(
        verbose_name="Tabla de Evolución Antropométrica",
        help_text="Registrar Fecha, Peso, Talla, IMC, C. Brazo, C. Cintura, C. Cadera, Pliegues (Triceps, Subescapular, Muslo anterior, Pantorrilla, Suprailiaco, Abdominal), Σ Pliegues, AM, AG",
        null=True, blank=True
    )
    dx_nutricional = models.TextField(verbose_name="Dx Nutricional", null=True, blank=True)
    req_rct = models.FloatField(verbose_name="Requerimiento Calórico: RCT", null=True, blank=True)
    req_kcal_kg = models.FloatField(verbose_name="Requerimiento (kcal/kg)", null=True, blank=True)
    req_cho_porc = models.FloatField(verbose_name="CHO (%)", null=True, blank=True)
    req_prot_porc = models.FloatField(verbose_name="Prot (%)", null=True, blank=True)
    req_grasa_porc = models.FloatField(verbose_name="Grasa (%)", null=True, blank=True)
    observaciones = models.TextField(verbose_name="Observaciones", null=True, blank=True)
    evolucion = models.TextField(verbose_name="Evolución", null=True, blank=True)

    class Meta:
        verbose_name = "Formato: Historia de Nutrición (Pág. 1 y 3)"
        verbose_name_plural = "Formatos: Historias de Nutrición (Pág. 1 y 3)"

    def __str__(self):
        return f"H. Nutrición de: {self.historial_padre.paciente}"


# -----------------------------------------------------------------------------
# 3. MODELOS PARA DOCUMENTOS EXPORTABLES (Sin cambios)
# -----------------------------------------------------------------------------
class DocumentoJustificativo(models.Model):
    historial_padre = models.ForeignKey(HistorialMedico, on_delete=models.CASCADE, related_name="justificativos")
    motivo_consulta = models.TextField(verbose_name="Motivo de Consulta", null=True, blank=True)
    hora_entrada = models.TimeField(verbose_name="Horario de", null=True, blank=True)
    hora_salida = models.TimeField(verbose_name="Horario a", null=True, blank=True)
    class Meta: verbose_name = "Documento: Justificativo"; verbose_name_plural = "Documentos: Justificativos"
    def __str__(self): return f"Justificativo ({self.historial_padre.fecha.strftime('%d/%m/%Y')}) para {self.historial_padre.paciente}"

class DocumentoReferencia(models.Model):
    historial_padre = models.ForeignKey(HistorialMedico, on_delete=models.CASCADE, related_name="referencias")
    referido_a = models.CharField(max_length=255, verbose_name="Referido a Consulta", null=True, blank=True)
    class Meta: verbose_name = "Documento: Referencia"; verbose_name_plural = "Documentos: Referencias"
    def __str__(self): return f"Referencia a {self.referido_a} para {self.historial_padre.paciente}"

class DocumentoReposo(models.Model):
    historial_padre = models.ForeignKey(HistorialMedico, on_delete=models.CASCADE, related_name="reposos")
    consulta = models.CharField(max_length=255, verbose_name="Consulta", null=True, blank=True)
    diagnostico = models.TextField(verbose_name="Diagnóstico", null=True, blank=True)
    duracion_dias = models.IntegerField(verbose_name="Duración (Días)", null=True, blank=True)
    fecha_inicio = models.DateField(verbose_name="Del", null=True, blank=True)
    fecha_fin = models.DateField(verbose_name="Al", null=True, blank=True)
    debe_volver = models.DateField(verbose_name="Debe volver", null=True, blank=True)
    class Meta: verbose_name = "Documento: Reposo"; verbose_name_plural = "Documentos: Reposos"
    def __str__(self): return f"Reposo ({self.duracion_dias or 'N/D'} días) para {self.historial_padre.paciente}"

class DocumentoRecipe(models.Model):
    historial_padre = models.ForeignKey(HistorialMedico, on_delete=models.CASCADE, related_name="recipes")
    texto_recipe = models.TextField(verbose_name="Récipe / Indicaciones", null=True, blank=True)
    class Meta: verbose_name = "Documento: Récipe/Indicaciones"; verbose_name_plural = "Documentos: Récipes/Indicaciones"
    def __str__(self): return f"Récipe ({self.historial_padre.fecha.strftime('%d/%m/%Y')}) para {self.historial_padre.paciente}"