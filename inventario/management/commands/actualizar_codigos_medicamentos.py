from django.core.management.base import BaseCommand
from inventario.models import Medicamento

class Command(BaseCommand):
    help = 'Actualiza los códigos de los medicamentos existentes'

    def handle(self, *args, **options):
        # Obtener todos los medicamentos sin código o con código vacío
        medicamentos = Medicamento.objects.filter(codigo='').order_by('id')
        
        self.stdout.write(
            self.style.NOTICE(f'Encontrados {medicamentos.count()} medicamentos sin código')
        )
        
        # Actualizar cada medicamento para generar su código
        for medicamento in medicamentos:
            # Forzar la regeneración del código
            medicamento.codigo = ''  # Vaciar el código para forzar la regeneración
            medicamento.save()
            self.stdout.write(
                self.style.SUCCESS(f'Actualizado: {medicamento.nombre} -> {medicamento.codigo}')
            )
        
        self.stdout.write(
            self.style.SUCCESS('Todos los medicamentos han sido actualizados con códigos')
        )