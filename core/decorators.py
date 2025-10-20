from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib import messages
from functools import wraps

def role_required(allowed_roles=[]):
    """
    Decorador para vistas basadas en funciones que comprueba si el usuario tiene uno de los roles permitidos o es un superusuario.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(reverse_lazy('core:login'))

            # Los superusuarios siempre tienen acceso
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            # Si el perfil del usuario está en los roles permitidos, se ejecuta la vista
            if hasattr(request.user, 'perfilusuario') and request.user.perfilusuario.rol in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                # Si no tiene el rol, se muestra un mensaje y se redirige
                messages.error(request, 'No tienes los permisos necesarios para acceder a esta página.')
                return redirect(reverse_lazy('core:acceso_denegado'))
        return _wrapped_view
    return decorator


class RoleRequiredMixin(UserPassesTestMixin):
    """
    Mixin para vistas basadas en clases que comprueba si el usuario tiene un rol permitido.
    Se debe definir `allowed_roles` en la vista que herede de este mixin.
    """
    allowed_roles = []
    login_url = reverse_lazy('core:login')
    permission_denied_message = 'No tienes los permisos necesarios para acceder a esta página.'

    def test_func(self):
        """Comprueba si el rol del usuario está en la lista de roles permitidos o si es superusuario."""
        if not self.request.user.is_authenticated:
            return False
        
        # Los superusuarios siempre tienen acceso
        if self.request.user.is_superuser:
            return True
            
        if hasattr(self.request.user, 'perfilusuario'):
            return self.request.user.perfilusuario.rol in self.allowed_roles
        return False

    def handle_no_permission(self):
        """
        Redirige al usuario a la página de acceso denegado si no tiene permiso.
        """
        messages.error(self.request, self.permission_denied_message)
        return redirect(reverse_lazy('core:acceso_denegado'))


# --- Mixins específicos para cada rol ---

class AdminRequiredMixin(RoleRequiredMixin):
    """Acceso solo para administradores."""
    allowed_roles = ['admin']

class MedicoRequiredMixin(RoleRequiredMixin):
    """Acceso para médicos y administradores."""
    allowed_roles = ['admin', 'medico']

class RecepcionistaRequiredMixin(RoleRequiredMixin):
    """Acceso para recepcionistas y administradores."""
    allowed_roles = ['admin', 'recepcionista']

class PersonalMedicoRequiredMixin(RoleRequiredMixin):
    """Acceso para médicos, recepcionistas y administradores."""
    allowed_roles = ['admin', 'medico', 'recepcionista']


# --- Decoradores específicos para cada rol ---

admin_required = role_required(allowed_roles=['admin'])
medico_required = role_required(allowed_roles=['admin', 'medico'])
recepcionista_required = role_required(allowed_roles=['admin', 'recepcionista'])
personal_medico_required = role_required(allowed_roles=['admin', 'medico', 'recepcionista'])
