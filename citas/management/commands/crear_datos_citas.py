from django.core.management.base import BaseCommand
from citas.models import EstadoCita, TipoCita, MotivoCita

class Command(BaseCommand):
    help = 'Crea datos iniciales para citas'

    def handle(self, *args, **options):
        # Crear estados de cita iniciales (versión simplificada)
        estados = [
            {'nombre': 'Programada', 'descripcion': 'Cita programada pero aún no atendida', 'color': '#007bff'},
            {'nombre': 'Cancelada', 'descripcion': 'Cita cancelada por el paciente o el médico', 'color': '#dc3545'},
            {'nombre': 'Completada', 'descripcion': 'Cita atendida y finalizada', 'color': '#28a745'},
            {'nombre': 'No asistió', 'descripcion': 'El paciente no asistió a la cita', 'color': '#ffc107'},
        ]
        
        for estado_data in estados:
            estado, created = EstadoCita.objects.get_or_create(
                nombre=estado_data['nombre'],
                defaults={
                    'descripcion': estado_data['descripcion'],
                    'color': estado_data['color']
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Estado de cita "{estado.nombre}" creado exitosamente')
                )
            else:
                self.stdout.write(
                    self.style.NOTICE(f'Estado de cita "{estado.nombre}" ya existe')
                )
        
        # Crear tipos de cita iniciales
        tipos = [
            {'nombre': 'Consulta médica', 'descripcion': 'Consulta médica general', 'duracion_estimada': 30},
            {'nombre': 'Revisión', 'descripcion': 'Revisión de tratamiento o evolución', 'duracion_estimada': 20},
            {'nombre': 'Emergencia', 'descripcion': 'Atención de emergencia médica', 'duracion_estimada': 60},
            {'nombre': 'Control', 'descripcion': 'Control de seguimiento', 'duracion_estimada': 15},
        ]
        
        for tipo_data in tipos:
            tipo, created = TipoCita.objects.get_or_create(
                nombre=tipo_data['nombre'],
                defaults={
                    'descripcion': tipo_data['descripcion'],
                    'duracion_estimada': tipo_data['duracion_estimada']
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Tipo de cita "{tipo.nombre}" creado exitosamente')
                )
            else:
                self.stdout.write(
                    self.style.NOTICE(f'Tipo de cita "{tipo.nombre}" ya existe')
                )
        
        # Crear motivos de cita iniciales
        motivos = [
            {'nombre': 'Chequeo general', 'descripcion': 'Revisión médica general de rutina'},
            {'nombre': 'Dolor abdominal', 'descripcion': 'Dolor o molestias en la zona abdominal'},
            {'nombre': 'Fiebre', 'descripcion': 'Presencia de fiebre persistente'},
            {'nombre': 'Dolor de cabeza', 'descripcion': 'Dolor de cabeza o migraña'},
            {'nombre': 'Problemas respiratorios', 'descripcion': 'Dificultad para respirar o tos persistente'},
            {'nombre': 'Seguimiento', 'descripcion': 'Seguimiento de tratamiento médico'},
            {'nombre': 'Vacunación', 'descripcion': 'Administración de vacunas'},
        ]
        
        for motivo_data in motivos:
            motivo, created = MotivoCita.objects.get_or_create(
                nombre=motivo_data['nombre'],
                defaults={
                    'descripcion': motivo_data['descripcion']
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Motivo de cita "{motivo.nombre}" creado exitosamente')
                )
            else:
                self.stdout.write(
                    self.style.NOTICE(f'Motivo de cita "{motivo.nombre}" ya existe')
                )
        
        self.stdout.write(
            self.style.SUCCESS('Datos iniciales para citas creados exitosamente')
        )