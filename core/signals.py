from django.db.models.signals import post_save
from django.contrib.auth.models import User, Group
from django.dispatch import receiver
from .models import PerfilUsuario


@receiver(post_save, sender=PerfilUsuario)
def actualizar_grupo_por_rol(sender, instance, **kwargs):
    """
    Actualiza el grupo del usuario cuando se cambia su rol
    """
    usuario = instance.usuario
    
    # Limpiar grupos anteriores
    usuario.groups.clear()
    
    # Asignar al grupo correspondiente según el rol
    if instance.rol == 'admin':
        grupo, created = Group.objects.get_or_create(name='Administradores')
    elif instance.rol == 'medico':
        grupo, created = Group.objects.get_or_create(name='Medicos')
    else:  # recepcionista
        grupo, created = Group.objects.get_or_create(name='Recepcionistas')
    
    usuario.groups.add(grupo)