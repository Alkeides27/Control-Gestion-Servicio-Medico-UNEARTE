from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin
from .models import PerfilUsuario


class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfiles de Usuario'


class UsuarioAdmin(UserAdmin):
    inlines = (PerfilUsuarioInline,)


# Reemplazar la administración de usuarios predeterminada
admin.site.unregister(User) if admin.site.is_registered(User) else None
admin.site.register(User, UsuarioAdmin)

# Registrar el modelo de PerfilUsuario también
@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'rol', 'created_at')
    list_filter = ('rol', 'created_at')
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__last_name')
    readonly_fields = ('created_at', 'updated_at')
