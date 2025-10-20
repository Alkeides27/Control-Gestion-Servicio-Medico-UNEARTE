from django.db import models
from pacientes.models import Paciente
from inventario.models import Medicamento

# Nuevo modelo para Alergias
class Alergia(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True, help_text="Descripción o notas sobre la alergia.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'historiales_alergias'
        verbose_name = 'Alergia'
        verbose_name_plural = 'Alergias'
        ordering = ['nombre']

# Nuevo modelo para Enfermedades
class Enfermedad(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    descripcion = models.TextField(blank=True, null=True, help_text="Descripción o notas sobre la enfermedad.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'historiales_enfermedades'
        verbose_name = 'Enfermedad'
        verbose_name_plural = 'Enfermedades'
        ordering = ['nombre']

# Modelo HistorialMedico modificado
class HistorialMedico(models.Model):
    paciente = models.OneToOneField(Paciente, on_delete=models.CASCADE, related_name='historial_medico')
    
    # Campos ManyToManyField para relaciones estructuradas
    alergias = models.ManyToManyField(Alergia, blank=True, related_name='historiales')
    enfermedades_preexistentes = models.ManyToManyField(Enfermedad, blank=True, related_name='historiales')
    medicamentos_actuales = models.ManyToManyField(Medicamento, blank=True, related_name='historiales_medicamentos')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Historial de {self.paciente}"
    
    class Meta:
        db_table = 'historiales_medicos'
        verbose_name = 'Historial Médico'
        verbose_name_plural = 'Historiales Médicos'
