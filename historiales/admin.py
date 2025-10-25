from django.contrib import admin
from .models import HistorialMedico

@admin.register(HistorialMedico)
class HistorialMedicoAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'medico', 'fecha')
    search_fields = ('paciente__nombre', 'paciente__apellido', 'paciente__numero_documento', 'medico__username')
    readonly_fields = ()