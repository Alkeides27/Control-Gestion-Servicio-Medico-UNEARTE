from django.contrib.auth.models import User
from django.db import models
from pacientes.models import Paciente
from django.utils import timezone

# -----------------------------------------------------------------------------
# FASE 3: RE-ARQUITECTURA DE MODELOS (VERSIÓN FINAL BASADA EN TXT 26/10/2025)
# -----------------------------------------------------------------------------

# 1. EL CONTENEDOR PRINCIPAL (Sesión Clínica)
# Mantenemos este modelo simple.
class HistorialMedico(models.Model):
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        verbose_name="Paciente"
    )
    medico = models.ForeignKey(
        User,
        on_delete=models.SET_NULL, # Si se borra el médico, el historial persiste
        null=True,
        blank=True,
        verbose_name="Médico Tratante"
    )
    fecha = models.DateTimeField(
        default=timezone.now,
        verbose_name="Fecha de Consulta"
    )
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Historial (Contenedor)"
        verbose_name_plural = "Historiales (Contenedores)"
        ordering = ['fecha']

    def __str__(self):
        return f"Historial de {self.paciente} - {self.fecha.strftime('%d/%m/%Y')}"


# -----------------------------------------------------------------------------
# 2. LOS FORMATOS (Datos de la consulta)
# -----------------------------------------------------------------------------

# --- MODELO PARA HISTORIA GENERAL (Págs. 2 y 9 del TXT) ---
class HistoriaGeneral(models.Model):
    # Concatenación
    historial_padre = models.OneToOneField(
        HistorialMedico,
        on_delete=models.CASCADE,
        related_name="historia_general",
        verbose_name="Historial Padre"
    )
    
    # --- Campos de Pág. 2 y 9 ---
    # Datos de Pág. 9
    peso = models.FloatField(verbose_name="Peso (kg)", null=True, blank=True) # Campo 11 Pág 9
    talla = models.FloatField(verbose_name="Talla (cm)", null=True, blank=True) # Campo 12 Pág 9
    ta = models.CharField(max_length=50, verbose_name="Tensión Arterial (TA)", null=True, blank=True) # Campo 13 Pág 9
    
    # Antecedentes Pág 2 y 9
    antecedentes_familiares = models.TextField( # Campo 15 Pág 9 / Campo 10 Pág 2
        verbose_name="Antecedentes Familiares",
        help_text="Ej: Diabetes, Hepatitis, Cardiovascular, Respiratoria, Neurológica, Otra.",
        null=True, blank=True
    )
    antecedentes_personales = models.TextField( # Campo 15 Pág 9 / Campo 11 Pág 2
        verbose_name="Antecedentes Personales",
        help_text="Ej: Diabetes, Hepatitis, Cardiovascular, Respiratoria, Neurológica, Cirugía, Alergias, ITS, Osteomusculares, Hábitos.",
        null=True, blank=True
    )
    
    # Historia Médica Pág 2 y 9
    motivo_consulta = models.TextField(verbose_name="Motivo de Consulta", null=True, blank=True) # Campo 16 Pág 9 / Campo 12 Pág 2
    enfermedad_actual = models.TextField(verbose_name="Enfermedad Actual", null=True, blank=True) # Campo 13 Pág 2
    # HEA de Pág 9 no está claramente definido en el TXT, podría ser parte de Enfermedad Actual o Motivo Consulta
    
    # Examen y Plan Pág 9
    examen_fisico = models.TextField(verbose_name="Examen Físico (EXFIS)", null=True, blank=True) # Campo 18 Pág 9
    diagnostico = models.TextField(verbose_name="Impresión Diagnóstica (IDX)", null=True, blank=True) # Campo 19 Pág 9
    plan = models.TextField(verbose_name="Plan y Tratamiento", null=True, blank=True) # Campo 20 Pág 9

    class Meta:
        verbose_name = "Formato: Historia General"
        verbose_name_plural = "Formatos: Historias Generales"

    def __str__(self):
        return f"H. General de: {self.historial_padre.paciente}"


# --- MODELO PARA HISTORIA DE NUTRICIÓN (Págs. 1 y 3 del TXT) - CORREGIDO SEGÚN TXT ---
class HistoriaNutricion(models.Model):
    # Concatenación
    historial_padre = models.OneToOneField(
        HistorialMedico,
        on_delete=models.CASCADE,
        related_name="historia_nutricion",
        verbose_name="Historial Padre"
    )

    # --- Campos Pág. 1: Información Básica Adicional ---
    numero_historia_clinica = models.CharField(max_length=50, verbose_name="N° Historia Clínica", null=True, blank=True) # Campo 1
    # Nombre, Edad, Fecha Nac, CI, Teléfono, Dirección ya están en Paciente
    estado_civil = models.CharField(max_length=50, verbose_name="Est. (Estado Civil)", null=True, blank=True) # Campo 8
    empleo = models.CharField(max_length=100, verbose_name="Empleo", null=True, blank=True) # Campo 9
    es_docente = models.BooleanField(verbose_name="Docente", default=False) # Campo 10
    otros_basicos = models.TextField(verbose_name="Otros (Datos Básicos)", null=True, blank=True) # Campo 11
    ceca = models.CharField(max_length=100, verbose_name="C.E.C.A.", null=True, blank=True) # Campo 12
    mencion = models.CharField(max_length=100, verbose_name="Mención", null=True, blank=True) # Campo 13
    semestre = models.CharField(max_length=50, verbose_name="Semestre", null=True, blank=True) # Campo 14

    # --- Campos Pág. 1: Motivo de Consulta ---
    motivo_consulta_nutricion = models.TextField(verbose_name="Motivo de consulta (Nutrición)", null=True, blank=True) # Campo 16

    # --- Campos Pág. 1: Antecedentes Médicos (Booleanos para Checkboxes) ---
    # Personales (Campo 17)
    antp_diabetes = models.BooleanField(verbose_name="Diabetes (Pers.)", default=False)
    antp_hta = models.BooleanField(verbose_name="HTA (Pers.)", default=False)
    antp_cardiopatias = models.BooleanField(verbose_name="Cardiopatías (Pers.)", default=False)
    antp_cancer = models.BooleanField(verbose_name="Cáncer (Pers.)", default=False)
    antp_gastritis = models.BooleanField(verbose_name="Gastritis (Pers.)", default=False)
    antp_hipertiroidismo = models.BooleanField(verbose_name="Hipertiroidismo (Pers.)", default=False)
    antp_hipotiroidismo = models.BooleanField(verbose_name="Hipotiroidismo (Pers.)", default=False) # Añadido según PDF visual
    antp_otros = models.TextField(verbose_name="Otros Antecedentes Personales", null=True, blank=True)

    # Familiares (Campo 18)
    antf_diabetes = models.BooleanField(verbose_name="Diabetes (Fam.)", default=False)
    antf_hta = models.BooleanField(verbose_name="HTA (Fam.)", default=False)
    antf_cardiopatias = models.BooleanField(verbose_name="Cardiopatías (Fam.)", default=False)
    antf_cancer = models.BooleanField(verbose_name="Cáncer (Fam.)", default=False)
    antf_gastritis = models.BooleanField(verbose_name="Gastritis (Fam.)", default=False)
    antf_hipertiroidismo = models.BooleanField(verbose_name="Hipertiroidismo (Fam.)", default=False)
    antf_hipotiroidismo = models.BooleanField(verbose_name="Hipotiroidismo (Fam.)", default=False) # Añadido según PDF visual
    antf_otros = models.TextField(verbose_name="Otros Antecedentes Familiares", null=True, blank=True)

    # --- Campos Pág. 1: Hábitos y Estilo de Vida ---
    # Psicológicos (Campo 19)
    hab_cafeicos = models.CharField(max_length=255, verbose_name="Café/Colas", null=True, blank=True)
    hab_cigarros = models.CharField(max_length=255, verbose_name="Cigarros", null=True, blank=True)
    hab_oh = models.CharField(max_length=255, verbose_name="OH (Alcohol)", null=True, blank=True)
    hab_medicamentos = models.TextField(verbose_name="Medicamentos", null=True, blank=True)
    hab_sueno = models.CharField(max_length=255, verbose_name="Sueño", null=True, blank=True)
    hab_apetito = models.CharField(max_length=255, verbose_name="Apetito", null=True, blank=True)
    hab_act_fisica = models.CharField(max_length=255, verbose_name="Actividad Física", null=True, blank=True)

    # Alimentarios (Campo 20)
    alim_n_comidas_dia = models.IntegerField(verbose_name="Nº Comidas/día", null=True, blank=True)
    alim_n_meriendas_dia = models.IntegerField(verbose_name="Nº Meriendas/día", null=True, blank=True)
    alim_hidricos_vasos_dia = models.IntegerField(verbose_name="Hidratación: Vasos/día", null=True, blank=True)
    alim_alergias = models.TextField(verbose_name="Alergias Alimentarias", null=True, blank=True)
    alim_intolerancias = models.TextField(verbose_name="Intolerancias Alimentarias", null=True, blank=True)

    # --- Campos Pág. 1: Examen Funcional ---
    # Checkboxes (Campo 21)
    func_masticacion = models.BooleanField(verbose_name="Masticación Dificultosa", default=False)
    func_disfagia = models.BooleanField(verbose_name="Disfagia", default=False)
    func_nauseas = models.BooleanField(verbose_name="Náuseas", default=False)
    func_vomitos = models.BooleanField(verbose_name="Vómitos", default=False)
    func_pirosis = models.BooleanField(verbose_name="Pirosis", default=False)
    func_rge = models.BooleanField(verbose_name="RGE", default=False)
    func_periodos_menstruales = models.BooleanField(verbose_name="Síntomas Períodos Menstruales", default=False)

    # Texto (Campos 22 y 23)
    func_micciones = models.CharField(max_length=255, verbose_name="Micciones", null=True, blank=True)
    func_evacuaciones = models.CharField(max_length=255, verbose_name="Evacuaciones", null=True, blank=True)

    # --- Campos Pág. 1: Frecuencia de Consumo de Alimentos ---
    FREC_CHOICES = [
        ('', '---------'), # Opción vacía
        ('D', 'Diario'),
        ('S', 'Semanal'),
        ('M', 'Mensual'),
        ('O', 'Ocasional'),
        ('N', 'Nunca'),
    ]
    
    # Lista 1
    frec_leche_comp = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Leche Comp.", null=True, blank=True)
    frec_leche_des = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Leche Des.", null=True, blank=True)
    frec_yogurt_nat = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Yogurt Nat.", null=True, blank=True)
    frec_yogurt_des = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Yogurt Des.", null=True, blank=True)
    
    # Lista 2
    frec_vegetales_crudos = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Vegetales Crudos", null=True, blank=True)
    frec_vegetales_cocidos = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Vegetales Cocidos", null=True, blank=True)
    frec_vegetales_licuados = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Vegetales Licuados", null=True, blank=True)
    
    # Lista 3
    frec_frutas_enteras = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Frutas Enteras", null=True, blank=True)
    frec_frutas_licuadas = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Frutas Licuadas", null=True, blank=True)
    
    # Lista 4
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
    frec_dulces_lista4 = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Dulces (Lista 4)", null=True, blank=True) # Renombrado
    frec_salados = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Salados (Snacks)", null=True, blank=True)
    
    # Lista 5
    frec_pollo_c_piel = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Pollo c/piel", null=True, blank=True)
    frec_pollo_s_piel = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Pollo s/piel", null=True, blank=True) # Según PDF visual
    frec_pescado = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Pescado", null=True, blank=True)
    frec_res = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Res", null=True, blank=True)
    frec_pavo = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Pavo", null=True, blank=True) # Según PDF visual
    frec_cerdo = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Cerdo", null=True, blank=True)
    frec_huevos = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Huevos", null=True, blank=True)
    frec_embutidos = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Embutidos", null=True, blank=True)
    frec_visceras = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Vísceras", null=True, blank=True)
    frec_otros_lista5 = models.CharField(max_length=100, verbose_name="Otros (Lista 5)", null=True, blank=True) # Renombrado
    
    # Lista 6
    frec_aceite = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Aceite", null=True, blank=True)
    frec_mayonesa = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Mayonesa", null=True, blank=True)
    frec_mantequilla = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Mantequilla", null=True, blank=True)
    frec_margarina = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Margarina", null=True, blank=True)
    frec_frutos_secos = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Frutos Secos", null=True, blank=True)
    frec_frituras = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Frituras", null=True, blank=True)
    # No hay otros en lista 6 en PDF visual / TXT

    # Otros (final)
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

    # --- Campos Pág. 1: Recordatorio 24 Horas ---
    recordatorio_24h_d = models.TextField(verbose_name="Recordatorio 24h (Desayuno)", null=True, blank=True)
    recordatorio_24h_m1 = models.TextField(verbose_name="Recordatorio 24h (Media Mañana)", null=True, blank=True)
    recordatorio_24h_a = models.TextField(verbose_name="Recordatorio 24h (Almuerzo)", null=True, blank=True)
    recordatorio_24h_m2 = models.TextField(verbose_name="Recordatorio 24h (Media Tarde)", null=True, blank=True) # Asumiendo Media Tarde
    recordatorio_24h_c = models.TextField(verbose_name="Recordatorio 24h (Cena)", null=True, blank=True)

    # --- Campos Pág. 3: Datos Laboratorio ---
    datos_laboratorio = models.TextField(verbose_name="Datos Laboratorio", null=True, blank=True) # Campo 1 Pág 3

    # --- Campos Pág. 3: Datos Antropométricos ---
    antropo_peso_usual = models.FloatField(verbose_name="Peso Usual (kg)", null=True, blank=True) # Campo 2 Pág 3
    antropo_peso_graso = models.FloatField(verbose_name="Peso Graso (kg)", null=True, blank=True) # Campo 3 Pág 3
    antropo_peso_max = models.FloatField(verbose_name="Peso Máx (kg)", null=True, blank=True) # Campo 4 Pág 3
    antropo_peso_magro = models.FloatField(verbose_name="Peso Magro (kg)", null=True, blank=True) # Campo 5 Pág 3
    antropo_peso_min = models.FloatField(verbose_name="Peso Mín (kg)", null=True, blank=True) # Campo 6 Pág 3
    antropo_porc_grasa = models.FloatField(verbose_name="% Grasa", null=True, blank=True) # Campo 7 Pág 3
    antropo_porc_grasa_rcom = models.FloatField(verbose_name="% Grasa Recomendado", null=True, blank=True) # Campo 8 Pág 3
    antropo_peso_rcom = models.FloatField(verbose_name="Peso Recomendado (kg)", null=True, blank=True) # Campo 9 Pág 3

    # --- Campos Pág. 3: Tabla Antropométrica ---
    # Usamos TextField. El help_text indica los campos esperados.
    tabla_antropometrica = models.TextField( # Campo 10 Pág 3
        verbose_name="Tabla de Evolución Antropométrica",
        help_text="Registrar Fecha, Peso, Talla, IMC, C. Brazo, C. Cintura, C. Cadera, Pliegues (Triceps, Subescapular, Muslo anterior, Pantorrilla, Suprailiaco, Abdominal), Σ Pliegues, AM, AG",
        null=True, blank=True
    )

    # --- Campos Pág. 3: Diagnóstico y Requerimiento ---
    dx_nutricional = models.TextField(verbose_name="Dx Nutricional", null=True, blank=True) # Campo 11 Pág 3
    req_rct = models.FloatField(verbose_name="Requerimiento Calórico: RCT", null=True, blank=True) # Campo 12 Pág 3
    req_kcal_kg = models.FloatField(verbose_name="Requerimiento (kcal/kg)", null=True, blank=True) # Campo 13 Pág 3
    req_cho_porc = models.FloatField(verbose_name="CHO (%)", null=True, blank=True) # Campo 14 Pág 3
    req_prot_porc = models.FloatField(verbose_name="Prot (%)", null=True, blank=True) # Campo 15 Pág 3
    req_grasa_porc = models.FloatField(verbose_name="Grasa (%)", null=True, blank=True) # Campo 16 Pág 3
    
    # --- Campos Pág. 3: Observaciones y Evolución ---
    observaciones = models.TextField(verbose_name="Observaciones", null=True, blank=True) # Campo 17 Pág 3
    evolucion = models.TextField(verbose_name="Evolución", null=True, blank=True) # Campo 18 Pág 3
    
    class Meta:
        verbose_name = "Formato: Historia de Nutrición"
        verbose_name_plural = "Formatos: Historias de Nutrición"

    def __str__(self):
        return f"H. Nutrición de: {self.historial_padre.paciente}"


# -----------------------------------------------------------------------------
# 3. MODELOS PARA DOCUMENTOS EXPORTABLES (Basados en TXT Págs. 4-8)
# -----------------------------------------------------------------------------

# --- MODELO PARA JUSTIFICATIVO (Pág. 4) ---
class DocumentoJustificativo(models.Model):
    historial_padre = models.ForeignKey(HistorialMedico, on_delete=models.CASCADE, related_name="justificativos")
    # Fecha, Apellidos/Nombres, Cédula se obtienen del historial_padre y su paciente
    motivo_consulta = models.TextField(verbose_name="Motivo de Consulta", null=True, blank=True) # Campo 5 Pág 4
    hora_entrada = models.TimeField(verbose_name="Horario de", null=True, blank=True) # Campo 4 Pág 4
    hora_salida = models.TimeField(verbose_name="Horario a", null=True, blank=True) # Campo 4 Pág 4
    
    class Meta:
        verbose_name = "Documento: Justificativo"
        verbose_name_plural = "Documentos: Justificativos"
    
    def __str__(self):
        return f"Justificativo ({self.historial_padre.fecha.strftime('%d/%m/%Y')}) para {self.historial_padre.paciente}"

# --- MODELO PARA REFERENCIA (Pág. 5) ---
class DocumentoReferencia(models.Model):
    historial_padre = models.ForeignKey(HistorialMedico, on_delete=models.CASCADE, related_name="referencias")
    # Fecha, Apellidos/Nombres, Cédula se obtienen del historial_padre y su paciente
    referido_a = models.CharField(max_length=255, verbose_name="Referido a Consulta", null=True, blank=True) # Campo 4 Pág 5
    # Añadimos un motivo, aunque el PDF/TXT no lo tiene explícito, es necesario
    motivo_referencia = models.TextField(verbose_name="Motivo de Referencia", null=True, blank=True)

    class Meta:
        verbose_name = "Documento: Referencia"
        verbose_name_plural = "Documentos: Referencias"

    def __str__(self):
        return f"Referencia a {self.referido_a} para {self.historial_padre.paciente}"

# --- MODELO PARA REPOSO (Pág. 6) ---
class DocumentoReposo(models.Model):
    historial_padre = models.ForeignKey(HistorialMedico, on_delete=models.CASCADE, related_name="reposos")
    # Fecha, Apellidos/Nombres, Cédula se obtienen del historial_padre y su paciente
    consulta = models.CharField(max_length=255, verbose_name="Consulta", null=True, blank=True) # Campo 4 Pág 6
    diagnostico = models.TextField(verbose_name="Diagnóstico", null=True, blank=True) # Campo 5 Pág 6
    duracion_dias = models.IntegerField(verbose_name="Duración (Días)", null=True, blank=True) # Campo 6 Pág 6
    fecha_inicio = models.DateField(verbose_name="Del", null=True, blank=True) # Campo 7 Pág 6
    fecha_fin = models.DateField(verbose_name="Al", null=True, blank=True) # Campo 7 Pág 6
    debe_volver = models.DateField(verbose_name="Debe volver", null=True, blank=True) # Campo 8 Pág 6

    class Meta:
        verbose_name = "Documento: Reposo"
        verbose_name_plural = "Documentos: Reposos"

    def __str__(self):
        return f"Reposo ({self.duracion_dias or 'N/D'} días) para {self.historial_padre.paciente}"

# --- MODELO PARA RÉCIPE / INDICACIONES (Pág. 7 y 8) ---
class DocumentoRecipe(models.Model):
    historial_padre = models.ForeignKey(HistorialMedico, on_delete=models.CASCADE, related_name="recipes")
    # Fecha, Apellidos/Nombres, Cédula, Edad se obtienen del historial_padre y su paciente
    texto_recipe = models.TextField(verbose_name="Récipe / Indicaciones", null=True, blank=True) # Campo 7 Pág 7 / Campo 6 Pág 8

    class Meta:
        verbose_name = "Documento: Récipe/Indicaciones"
        verbose_name_plural = "Documentos: Récipes/Indicaciones"
    
    def __str__(self):
        return f"Récipe ({self.historial_padre.fecha.strftime('%d/%m/%Y')}) para {self.historial_padre.paciente}"
