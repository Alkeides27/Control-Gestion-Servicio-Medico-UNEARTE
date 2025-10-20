from django.core.management.base import BaseCommand
from inventario.models import Categoria, Proveedor, Medicamento, Inventario
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Crea datos de ejemplo para el sistema de inventario'

    def handle(self, *args, **options):
        # Crear categorías
        categoria_analgesicos, created = Categoria.objects.get_or_create(
            nombre='Analgésicos',
            defaults={'descripcion': 'Medicamentos para el alivio del dolor'}
        )
        
        categoria_antibioticos, created = Categoria.objects.get_or_create(
            nombre='Antibióticos',
            defaults={'descripcion': 'Medicamentos para combatir infecciones bacterianas'}
        )
        
        categoria_vitaminas, created = Categoria.objects.get_or_create(
            nombre='Vitaminas',
            defaults={'descripcion': 'Suplementos vitamínicos'}
        )
        
        self.stdout.write(
            self.style.SUCCESS('Categorías creadas exitosamente')
        )
        
        # Crear proveedores
        proveedor_farmaceutica, created = Proveedor.objects.get_or_create(
            nombre='Farmacéutica Nacional',
            defaults={
                'contacto': 'Juan Pérez',
                'telefono': '0212-1234567',
                'email': 'contacto@farmaceuticanacional.com',
                'direccion': 'Av. Principal, Edif. 123, Caracas'
            }
        )
        
        proveedor_medica, created = Proveedor.objects.get_or_create(
            nombre='Médica Distribuidora',
            defaults={
                'contacto': 'María González',
                'telefono': '0212-7654321',
                'email': 'ventas@medicadistribuidora.com',
                'direccion': 'Calle Secundaria, Local 456, Caracas'
            }
        )
        
        self.stdout.write(
            self.style.SUCCESS('Proveedores creados exitosamente')
        )
        
        # Crear medicamentos
        medicamento_ibuprofeno, created = Medicamento.objects.get_or_create(
            codigo='MED-001',
            defaults={
                'nombre': 'Ibuprofeno 400mg',
                'descripcion': 'Antiinflamatorio no esteroideo',
                'categoria': categoria_analgesicos,
                'proveedor': proveedor_farmaceutica,
                'precio_unitario': 15.50,
                'stock_minimo': 20
            }
        )
        
        medicamento_paracetamol, created = Medicamento.objects.get_or_create(
            codigo='MED-002',
            defaults={
                'nombre': 'Paracetamol 500mg',
                'descripcion': 'Analgésico y antipirético',
                'categoria': categoria_analgesicos,
                'proveedor': proveedor_medica,
                'precio_unitario': 12.75,
                'stock_minimo': 30
            }
        )
        
        medicamento_amoxicilina, created = Medicamento.objects.get_or_create(
            codigo='MED-003',
            defaults={
                'nombre': 'Amoxicilina 500mg',
                'descripcion': 'Antibiótico de amplio espectro',
                'categoria': categoria_antibioticos,
                'proveedor': proveedor_farmaceutica,
                'precio_unitario': 22.30,
                'stock_minimo': 15
            }
        )
        
        medicamento_vitamina_c, created = Medicamento.objects.get_or_create(
            codigo='MED-004',
            defaults={
                'nombre': 'Vitamina C 1000mg',
                'descripcion': 'Suplemento vitamínico',
                'categoria': categoria_vitaminas,
                'proveedor': proveedor_medica,
                'precio_unitario': 18.90,
                'stock_minimo': 25
            }
        )
        
        self.stdout.write(
            self.style.SUCCESS('Medicamentos creados exitosamente')
        )
        
        # Crear existencias en inventario
        inventario_ibuprofeno, created = Inventario.objects.get_or_create(
            medicamento=medicamento_ibuprofeno,
            defaults={
                'cantidad': 50,
                'fecha_caducidad': date.today() + timedelta(days=365),
                'lote': 'LOT-001'
            }
        )
        
        inventario_paracetamol, created = Inventario.objects.get_or_create(
            medicamento=medicamento_paracetamol,
            defaults={
                'cantidad': 45,
                'fecha_caducidad': date.today() + timedelta(days=180),
                'lote': 'LOT-002'
            }
        )
        
        inventario_amoxicilina, created = Inventario.objects.get_or_create(
            medicamento=medicamento_amoxicilina,
            defaults={
                'cantidad': 30,
                'fecha_caducidad': date.today() + timedelta(days=90),
                'lote': 'LOT-003'
            }
        )
        
        inventario_vitamina_c, created = Inventario.objects.get_or_create(
            medicamento=medicamento_vitamina_c,
            defaults={
                'cantidad': 40,
                'fecha_caducidad': date.today() + timedelta(days=730),
                'lote': 'LOT-004'
            }
        )
        
        self.stdout.write(
            self.style.SUCCESS('Inventario inicial creado exitosamente')
        )
        
        self.stdout.write(
            self.style.SUCCESS('Todos los datos de ejemplo han sido creados exitosamente')
        )