from django.db import models
from pacientes.models import Paciente

class EstadoCita(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=7, blank=True, null=True)  # Código de color HEX
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        db_table = 'estados_cita'
        verbose_name = 'Estado de Cita'
        verbose_name_plural = 'Estados de Cita'

class TipoCita(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    duracion_estimada = models.IntegerField(help_text="Duración estimada en minutos", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        db_table = 'tipos_cita'
        verbose_name = 'Tipo de Cita'
        verbose_name_plural = 'Tipos de Cita'

class MotivoCita(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        db_table = 'motivos_cita'
        verbose_name = 'Motivo de Cita'
        verbose_name_plural = 'Motivos de Cita'

class Cita(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    tipo_cita = models.ForeignKey(TipoCita, on_delete=models.CASCADE)
    motivo = models.ForeignKey(MotivoCita, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    estado = models.ForeignKey(EstadoCita, on_delete=models.CASCADE)
    observaciones = models.TextField(blank=True, null=True, help_text="Observaciones generales de la cita")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cita de {self.paciente} el {self.fecha} a las {self.hora_inicio}"
    
    class Meta:
        db_table = 'citas'
        unique_together = ('paciente', 'fecha', 'hora_inicio')
        indexes = [
            models.Index(fields=['fecha', 'hora_inicio']),
            models.Index(fields=['estado']),
        ]
        verbose_name = 'Cita'
        verbose_name_plural = 'Citas'

class TipoNota(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        db_table = 'tipos_nota'
        verbose_name = 'Tipo de Nota'
        verbose_name_plural = 'Tipos de Nota'

class NotaCita(models.Model):
    cita = models.ForeignKey(Cita, on_delete=models.CASCADE, related_name='notas')
    tipo_nota = models.ForeignKey(TipoNota, on_delete=models.CASCADE)
    contenido = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Nota de {self.cita} - {self.tipo_nota.nombre}"
    
    class Meta:
        db_table = 'notas_cita'
        verbose_name = 'Nota de Cita'
        verbose_name_plural = 'Notas de Cita'