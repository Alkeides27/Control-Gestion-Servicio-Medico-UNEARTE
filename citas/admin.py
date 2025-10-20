from django.contrib import admin
from .models import EstadoCita, TipoCita, MotivoCita, Cita, TipoNota, NotaCita

@admin.register(EstadoCita)
class EstadoCitaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'color')
    search_fields = ('nombre',)

@admin.register(TipoCita)
class TipoCitaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'duracion_estimada')
    search_fields = ('nombre',)

@admin.register(MotivoCita)
class MotivoCitaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'tipo_cita', 'motivo', 'fecha', 'hora_inicio', 'estado')
    list_filter = ('estado', 'tipo_cita', 'motivo', 'fecha')
    search_fields = ('paciente__nombre', 'paciente__apellido', 'motivo__nombre')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(TipoNota)
class TipoNotaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(NotaCita)
class NotaCitaAdmin(admin.ModelAdmin):
    list_display = ('cita', 'tipo_nota', 'created_at')
    list_filter = ('tipo_nota', 'created_at')
    search_fields = ('cita__paciente__nombre', 'cita__paciente__apellido', 'tipo_nota__nombre')
    readonly_fields = ('created_at', 'updated_at')