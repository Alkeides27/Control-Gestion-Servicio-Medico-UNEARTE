from django.contrib.auth.models import User
from django.db import models
from pacientes.models import Paciente
from django.utils import timezone

# -----------------------------------------------------------------------------
# FASE 3: RE-ARQUITECTURA DE MODELOS
# -----------------------------------------------------------------------------

# 1. EL CONTENEDOR PRINCIPAL (Sesión Clínica)
# Este modelo ya existe, pero ahora solo actúa como un "contenedor".
# Los campos específicos (motivo_consulta, diagnostico, etc.) se MOVIERON a HistoriaGeneral.
# El campo 'paciente' fue cambiado de OneToOneField a ForeignKey en la Fase 2.
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
    # Campos de auditoría que ya deberías tener
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

# --- MODELO PARA HISTORIA GENERAL (Págs. 2 y 9 del PDF) ---
class HistoriaGeneral(models.Model):
    # Concatenación
    historial_padre = models.OneToOneField(
        HistorialMedico,
        on_delete=models.CASCADE,
        related_name="historia_general",
        verbose_name="Historial Padre"
    )
    
    # --- Campos de Pág. 2 y 9 ---
    # Datos por consulta
    peso = models.FloatField(verbose_name="Peso (kg)", null=True, blank=True)
    talla = models.FloatField(verbose_name="Talla (cm)", null=True, blank=True)
    ta = models.CharField(max_length=50, verbose_name="Tensión Arterial (TA)", null=True, blank=True)
    
    # Campos movidos desde el HistorialMedico original
    motivo_consulta = models.TextField(verbose_name="Motivo de Consulta", null=True, blank=True)
    enfermedad_actual = models.TextField(verbose_name="Enfermedad Actual (HEA)", null=True, blank=True)
    
    # Campo renombrado (antes "enfermedades_preexistentes")
    # Usamos TextField para que el médico escriba, basándose en los checkboxes del PDF (pág 2)
    antecedentes_personales = models.TextField(
        verbose_name="Antecedentes Personales",
        help_text="Ej: Diabetes, Hepatitis, Cardiovascular, Cirugías, Alergias, Hábitos, etc.",
        null=True, blank=True
    )
    # Campo para Antecedentes Familiares (pág 2 y 9)
    antecedentes_familiares = models.TextField(
        verbose_name="Antecedentes Familiares",
        help_text="Ej: Diabetes, HTA, Cardiopatías, Cáncer, etc.",
        null=True, blank=True
    )
    
    # Campos de Pág. 9
    examen_fisico = models.TextField(verbose_name="Examen Físico (EXFIS)", null=True, blank=True)
    diagnostico = models.TextField(verbose_name="Impresión Diagnóstica (IDX)", null=True, blank=True)
    plan = models.TextField(verbose_name="Plan y Tratamiento", null=True, blank=True)

    class Meta:
        verbose_name = "Formato: Historia General"
        verbose_name_plural = "Formatos: Historias Generales"

    def __str__(self):
        return f"H. General de: {self.historial_padre.paciente}"


# --- MODELO PARA HISTORIA DE NUTRICIÓN (Págs. 1 y 3 del PDF) ---
class HistoriaNutricion(models.Model):
    # Concatenación
    historial_padre = models.OneToOneField(
        HistorialMedico,
        on_delete=models.CASCADE,
        related_name="historia_nutricion",
        verbose_name="Historial Padre"
    )

    # --- Campos Pág. 1: Hábitos Psicobiológicos ---
    medicamentos = models.TextField(verbose_name="Medicamentos", null=True, blank=True)
    cafeicos = models.CharField(max_length=255, verbose_name="Cafeicos", null=True, blank=True)
    sueno = models.CharField(max_length=255, verbose_name="Sueño", null=True, blank=True)
    cigarros = models.CharField(max_length=255, verbose_name="Cigarros", null=True, blank=True)
    apetito = models.CharField(max_length=255, verbose_name="Apetito", null=True, blank=True)
    oh = models.CharField(max_length=255, verbose_name="Alcohol (OH)", null=True, blank=True)
    act_fisica = models.CharField(max_length=255, verbose_name="Actividad Física", null=True, blank=True)

    # --- Campos Pág. 1: Hábitos Alimentarios ---
    n_comidas_dia = models.IntegerField(verbose_name="Nº Comidas/día", null=True, blank=True)
    n_meriendas_dia = models.IntegerField(verbose_name="Nº Meriendas/día", null=True, blank=True)
    hidricos_vasos_dia = models.IntegerField(verbose_name="Hídricos (Vasos/días)", null=True, blank=True)
    alergias_alimentarias = models.TextField(verbose_name="Alergias Alimentarias", null=True, blank=True)
    intolerancias_alimentarias = models.TextField(verbose_name="Intolerancias Alimentarias", null=True, blank=True)

    # --- Campos Pág. 1: Examen Funcional (Checkboxes) ---
    funcional_masticacion = models.BooleanField(verbose_name="Masticación", default=False)
    funcional_disfagia = models.BooleanField(verbose_name="Disfagia", default=False)
    funcional_nauseas = models.BooleanField(verbose_name="Nauseas", default=False)
    funcional_vomitos = models.BooleanField(verbose_name="Vómitos", default=False)
    funcional_pirosis = models.BooleanField(verbose_name="Pirosis", default=False)
    funcional_rge = models.BooleanField(verbose_name="RGE", default=False)
    
    # --- Campos Pág. 1: Otros ---
    micciones = models.CharField(max_length=255, verbose_name="Micciones", null=True, blank=True)
    periodos_menstruales = models.CharField(max_length=255, verbose_name="Periodos Menstruales", null=True, blank=True)
    evacuaciones = models.CharField(max_length=255, verbose_name="Evacuaciones", null=True, blank=True)

    # --- Campos Pág. 1: Frecuencia de Consumo ---
    # Usaremos TextField para que el médico escriba la frecuencia (Diario, Semanal, etc.)
    FREC_CHOICES = [
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
    
    # Lista 2 (Dota 2)
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
    frec_tuberculos = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Tubérculos", null=True, blank=True)
    frec_platano = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Plátano", null=True, blank=True)
    frec_granos = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Granos", null=True, blank=True)
    frec_casabe = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Casabe", null=True, blank=True)
    
    # Lista 5
    frec_pollo_c_piel = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Pollo c/piel", null=True, blank=True)
    frec_pollo_s_piel = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Pollo s/piel", null=True, blank=True)
    frec_pescado = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Pescado", null=True, blank=True)
    frec_res = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Res", null=True, blank=True)
    frec_cerdo = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Cerdo", null=True, blank=True)
    frec_huevos = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Huevos", null=True, blank=True)
    frec_embutidos = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Embutidos", null=True, blank=True)
    frec_pavo = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Pavo", null=True, blank=True)
    frec_visceras = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Vísceras", null=True, blank=True)
    frec_otros_5 = models.CharField(max_length=100, verbose_name="Otros (Lista 5)", null=True, blank=True)
    
    # Lista 6
    frec_aceite = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Aceite", null=True, blank=True)
    frec_mayonesa = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Mayonesa", null=True, blank=True)
    frec_mantequilla = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Mantequilla", null=True, blank=True)
    frec_margarina = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Margarina", null=True, blank=True)
    frec_frutos_secos = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Frutos Secos", null=True, blank=True)
    frec_frituras = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Frituras", null=True, blank=True)
    frec_otros_6 = models.CharField(max_length=100, verbose_name="Otros (Lista 6)", null=True, blank=True)

    # Lista Adicional (Sin número)
    frec_galletas = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Galletas", null=True, blank=True)
    frec_dulces = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Dulces", null=True, blank=True)
    frec_salados = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Salados (Snacks)", null=True, blank=True)
    frec_azucar = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Azúcar", null=True, blank=True)
    frec_dulces_2 = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Dulces (Adicional)", null=True, blank=True)
    frec_refrescos = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Refrescos", null=True, blank=True)
    frec_jugos_envasados = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Jugos Envasados", null=True, blank=True)
    frec_malta = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Malta", null=True, blank=True)
    frec_te_frio = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Té Frío", null=True, blank=True)
    frec_sal = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Sal", null=True, blank=True)
    frec_enlatados = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Enlatados", null=True, blank=True)
    frec_cubitos = models.CharField(max_length=2, choices=FREC_CHOICES, verbose_name="Cubitos", null=True, blank=True)
    frec_otros_adicional = models.CharField(max_length=100, verbose_name="Otros (Adicional)", null=True, blank=True)

    # --- Campos Pág. 1: Recordatorio 24h ---
    recordatorio_24h_d = models.TextField(verbose_name="Recordatorio 24h (D)", null=True, blank=True)
    recordatorio_24h_m1 = models.TextField(verbose_name="Recordatorio 24h (M)", null=True, blank=True)
    recordatorio_24h_a = models.TextField(verbose_name="Recordatorio 24h (A)", null=True, blank=True)
    recordatorio_24h_m2 = models.TextField(verbose_name="Recordatorio 24h (M)", null=True, blank=True)
    recordatorio_24h_c = models.TextField(verbose_name="Recordatorio 24h (C)", null=True, blank=True)

    # --- Campos Pág. 3: Datos Laboratorio ---
    datos_laboratorio = models.TextField(verbose_name="Datos Laboratorio", null=True, blank=True)

    # --- Campos Pág. 3: Datos Antropométricos ---
    antropo_peso_usual = models.FloatField(verbose_name="Peso Usual (kg)", null=True, blank=True)
    antropo_peso_graso = models.FloatField(verbose_name="Peso Graso (kg)", null=True, blank=True)
    antropo_peso_max = models.FloatField(verbose_name="Peso Máx (kg)", null=True, blank=True)
    antropo_peso_magro = models.FloatField(verbose_name="Peso Magro (kg)", null=True, blank=True)
    antropo_peso_min = models.FloatField(verbose_name="Peso Mín (kg)", null=True, blank=True)
    antropo_porc_grasa = models.FloatField(verbose_name="% Grasa", null=True, blank=True)
    antropo_porc_grasa_rcom = models.FloatField(verbose_name="% Grasa Rcom", null=True, blank=True)
    antropo_peso_rcom = models.FloatField(verbose_name="Peso Rcom (kg)", null=True, blank=True)

    # --- Campos Pág. 3: Tabla Antropométrica ---
    # Usamos TextField para almacenar la tabla, o JSONField si tu DB lo soporta.
    # Por simplicidad, usaremos TextField.
    tabla_antropometrica = models.TextField(
        verbose_name="Tabla de Evolución Antropométrica",
        help_text="Registrar Fecha, Peso, Talla, IMC, C. Brazo, C. Cintura, C. Cadera, Pliegues, etc.",
        null=True, blank=True
    )

    # --- Campos Pág. 3: Diagnóstico y Requerimiento ---
    dx_nutricional = models.TextField(verbose_name="Dx Nutricional", null=True, blank=True)
    req_rct = models.FloatField(verbose_name="Requerimiento Calórico: RCT", null=True, blank=True)
    req_kcal_kg = models.FloatField(verbose_name="Requerimiento (kcal/kg)", null=True, blank=True)
    req_cho = models.FloatField(verbose_name="CHO (g)", null=True, blank=True)
    req_prot = models.FloatField(verbose_name="Prot (g)", null=True, blank=True)
    req_grasa = models.FloatField(verbose_name="Grasa (g)", null=True, blank=True)
    
    # --- Campos Pág. 3: Observaciones y Evolución ---
    observaciones = models.TextField(verbose_name="Observaciones", null=True, blank=True)
    evolucion = models.TextField(verbose_name="Evolución", null=True, blank=True)
    
    class Meta:
        verbose_name = "Formato: Historia de Nutrición"
        verbose_name_plural = "Formatos: Historias de Nutrición"

    def __str__(self):
        return f"H. Nutrición de: {self.historial_padre.paciente}"


# -----------------------------------------------------------------------------
# 3. MODELOS PARA DOCUMENTOS EXPORTABLES
# -----------------------------------------------------------------------------

# --- MODELO PARA JUSTIFICATIVO (Pág. 4) ---
class DocumentoJustificativo(models.Model):
    # Concatenación (Un historial puede tener varios)
    historial_padre = models.ForeignKey(
        HistorialMedico,
        on_delete=models.CASCADE,
        related_name="justificativos"
    )
    # Campos del PDF
    motivo_consulta = models.CharField(max_length=255, verbose_name="Motivo de Consulta", null=True, blank=True)
    hora_entrada = models.TimeField(verbose_name="Horario de", null=True, blank=True)
    hora_salida = models.TimeField(verbose_name="Horario a", null=True, blank=True)
    # 'dia' se puede obtener de historial_padre.fecha
    
    class Meta:
        verbose_name = "Documento: Justificativo"
        verbose_name_plural = "Documentos: Justificativos"
    
    def __str__(self):
        return f"Justificativo para {self.historial_padre.paciente}"

# --- MODELO PARA REFERENCIA (Pág. 5) ---
class DocumentoReferencia(models.Model):
    # Concatenación
    historial_padre = models.ForeignKey(
        HistorialMedico,
        on_delete=models.CASCADE,
        related_name="referencias"
    )
    # Campos del PDF
    referido_a = models.CharField(max_length=255, verbose_name="Referido a Consulta", null=True, blank=True)
    # Añadimos un motivo, aunque el PDF no lo tiene explícito, es necesario
    motivo_referencia = models.TextField(verbose_name="Motivo de Referencia", null=True, blank=True)

    class Meta:
        verbose_name = "Documento: Referencia"
        verbose_name_plural = "Documentos: Referencias"

    def __str__(self):
        return f"Referencia a {self.referido_a} para {self.historial_padre.paciente}"

# --- MODELO PARA REPOSO (Pág. 6) ---
class DocumentoReposo(models.Model):
    # Concatenación
    historial_padre = models.ForeignKey(
        HistorialMedico,
        on_delete=models.CASCADE,
        related_name="reposos"
    )
    # Campos del PDF
    consulta = models.CharField(max_length=255, verbose_name="Consulta", null=True, blank=True)
    diagnostico = models.CharField(max_length=255, verbose_name="Diagnóstico", null=True, blank=True)
    duracion_dias = models.IntegerField(verbose_name="Duración (Días)", null=True, blank=True)
    fecha_inicio = models.DateField(verbose_name="Del", null=True, blank=True)
    fecha_fin = models.DateField(verbose_name="Al", null=True, blank=True)
    debe_volver = models.DateField(verbose_name="Debe volver", null=True, blank=True)

    class Meta:
        verbose_name = "Documento: Reposo"
        verbose_name_plural = "Documentos: Reposos"

    def __str__(self):
        return f"Reposo ({self.duracion_dias} días) para {self.historial_padre.paciente}"

# --- MODELO PARA RÉCIPE / INDICACIONES (Pág. 7 y 8) ---
class DocumentoRecipe(models.Model):
    # Concatenación
    historial_padre = models.ForeignKey(
        HistorialMedico,
        on_delete=models.CASCADE,
        related_name="recipes"
    )
    # Campos del PDF (Indicaciones y Récipe son lo mismo)
    texto_recipe = models.TextField(verbose_name="Récipe / Indicaciones", null=True, blank=True)

    class Meta:
        verbose_name = "Documento: Récipe/Indicaciones"
        verbose_name_plural = "Documentos: Récipes/Indicaciones"
    
    def __str__(self):
        return f"Récipe para {self.historial_padre.paciente}"