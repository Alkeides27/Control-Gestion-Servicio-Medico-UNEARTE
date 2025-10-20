from django.contrib import admin
from .models import HistorialMedico

@admin.register(HistorialMedico)
class HistorialMedicoAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'created_at', 'updated_at')
    search_fields = ('paciente__nombre', 'paciente__apellido', 'paciente__numero_documento')
    readonly_fields = ('created_at', 'updated_at')