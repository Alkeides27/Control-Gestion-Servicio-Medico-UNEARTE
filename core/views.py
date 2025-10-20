from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, CreateView, ListView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.models import User, Group
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django import forms
from pacientes.models import Paciente
from citas.models import Cita
from historiales.models import HistorialMedico
from .models import PerfilUsuario
from django.utils import timezone
from django.db.models import Q


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas para el dashboard
        context['total_pacientes'] = Paciente.objects.count()
        context['citas_hoy'] = Cita.objects.filter(
            fecha=timezone.now().date()
        ).count()
        context['citas_pendientes'] = Cita.objects.filter(
            estado__nombre='Programada'
        ).count()
        context['total_historiales'] = HistorialMedico.objects.count()
        
        # Últimas citas
        context['ultimas_citas'] = Cita.objects.select_related(
            'paciente', 'estado', 'motivo'
        ).order_by('-fecha')[:5]
        
        # Últimos pacientes
        context['ultimos_pacientes'] = Paciente.objects.order_by('-created_at')[:5]
        
        return context


class AboutView(TemplateView):
    template_name = 'core/about.html'


class ContactView(TemplateView):
    template_name = 'core/contact.html'


class AccesoDenegadoView(LoginRequiredMixin, TemplateView):
    template_name = 'core/acceso_denegado.html'


class PerfilView(LoginRequiredMixin, TemplateView):
    template_name = 'core/perfil.html'


def handler404(request, exception):
    return render(request, 'core/404.html', status=404)


def handler500(request):
    return render(request, 'core/500.html', status=500)


@login_required
def search_all(request):
    query = request.GET.get('q', '')
    results = {
        'pacientes': [],
        'citas': [],
        'historiales': []
    }
    
    if query:
        # Buscar en pacientes (nombre, apellido, número de documento)
        results['pacientes'] = Paciente.objects.filter(
            Q(nombre__icontains=query) |
            Q(apellido__icontains=query) |
            Q(numero_documento__icontains=query)
        )
        
        # Buscar en citas (paciente asociado, motivo)
        # Primero obtengo los IDs de pacientes que coinciden
        paciente_ids = Paciente.objects.filter(
            Q(nombre__icontains=query) |
            Q(apellido__icontains=query)
        ).values_list('id', flat=True)
        
        results['citas'] = Cita.objects.filter(
            Q(paciente_id__in=paciente_ids) |
            Q(motivo__nombre__icontains=query) |
            Q(motivo__descripcion__icontains=query)
        ).select_related('paciente', 'estado', 'motivo')
        
        # Buscar en historiales (paciente asociado, información médica)
        # Primero obtengo los IDs de pacientes que coinciden
        paciente_ids_historial = Paciente.objects.filter(
            Q(nombre__icontains=query) |
            Q(apellido__icontains=query)
        ).values_list('id', flat=True)
        
        results['historiales'] = HistorialMedico.objects.filter(
            Q(paciente_id__in=paciente_ids_historial) |
            Q(alergias__nombre__icontains=query) |
            Q(enfermedades_preexistentes__nombre__icontains=query) |
            Q(medicamentos_actuales__nombre__icontains=query)
        ).select_related('paciente').distinct()
    
    # Limitar resultados para evitar páginas muy largas
    results['pacientes'] = results['pacientes'][:10]
    results['citas'] = results['citas'][:10]
    results['historiales'] = results['historiales'][:10]
    
    context = {
        'query': query,
        'results': results,
        'total_results': sum([
            len(results['pacientes']),
            len(results['citas']), 
            len(results['historiales'])
        ])
    }
    
    return render(request, 'core/search_results.html', context)


from .forms import LoginForm

class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('core:dashboard')


from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.contrib.auth import logout
from django.views import View
from django.views.generic import CreateView
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from .models import PerfilUsuario
from django.contrib import messages


class CustomLogoutView(View):
    template_name = 'registration/logged_out.html'
    
    def get(self, request, *args, **kwargs):
        # Muestra la página de confirmación previa al logout
        return render(request, self.template_name)
    
    def post(self, request, *args, **kwargs):
        # Procesa el logout y redirige
        logout(request)
        return HttpResponseRedirect(reverse_lazy('core:login'))


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}),
        }


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('core:login')
    template_name = 'registration/signup.html'
    
    def form_valid(self, form):
        # Guardar el usuario
        user = form.save()
        
        # Actualizar el rol en el perfil existente (creado por la señal)
        perfil = user.perfilusuario
        perfil.rol = 'recepcionista'
        perfil.save()
        
        # Asignar al grupo de Recepcionistas por defecto
        grupo, created = Group.objects.get_or_create(name='Recepcionistas')
        user.groups.add(grupo)
        
        messages.success(self.request, 'Usuario registrado exitosamente. Contacta con un administrador para que te asigne el rol adecuado.')
        
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Registro de Usuario'
        return context


from .decorators import AdminRequiredMixin, admin_required
from .forms import AdminUserCreationForm, AdminUserChangeForm
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, FormView
from django.contrib.auth.forms import SetPasswordForm


class UsuarioCreateView(AdminRequiredMixin, CreateView):
    form_class = AdminUserCreationForm
    template_name = 'registration/usuario_form.html'
    success_url = reverse_lazy('core:lista_usuarios')

    def form_valid(self, form):
        response = super().form_valid(form)
        rol = form.cleaned_data.get('rol')
        
        perfil = self.object.perfilusuario
        perfil.rol = rol
        perfil.save()
        
        grupo_nombre = rol.capitalize() if rol != 'recepcionista' else 'Recepcionista'
        grupo, created = Group.objects.get_or_create(name=grupo_nombre)
        
        self.object.groups.clear()
        self.object.groups.add(grupo)
        
        messages.success(self.request, f'Usuario {self.object.username} creado exitosamente.')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Crear Nuevo Usuario'
        return context


class UsuarioUpdateView(AdminRequiredMixin, UpdateView):
    model = User
    form_class = AdminUserChangeForm
    template_name = 'registration/usuario_form.html'
    success_url = reverse_lazy('core:lista_usuarios')

    def form_valid(self, form):
        response = super().form_valid(form)
        rol = form.cleaned_data.get('rol')
        
        perfil = self.object.perfilusuario
        perfil.rol = rol
        perfil.save()
        
        grupo_nombre = rol.capitalize() if rol != 'recepcionista' else 'Recepcionista'
        grupo, created = Group.objects.get_or_create(name=grupo_nombre)
        
        self.object.groups.clear()
        self.object.groups.add(grupo)
        
        messages.success(self.request, f'Usuario {self.object.username} actualizado exitosamente.')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Editar Usuario: {self.object.username}'
        return context


class UsuarioDeleteView(AdminRequiredMixin, DeleteView):
    model = User
    template_name = 'registration/usuario_confirm_delete.html'
    success_url = reverse_lazy('core:lista_usuarios')
    context_object_name = 'usuario'

    def get_queryset(self):
        return super().get_queryset().exclude(pk=self.request.user.pk)

    def form_valid(self, form):
        messages.success(self.request, f"Usuario {self.object.username} eliminado exitosamente.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Eliminar Usuario: {self.object.username}'
        return context


class UsuarioSetPasswordView(AdminRequiredMixin, FormView):
    form_class = SetPasswordForm
    template_name = 'registration/usuario_set_password.html'
    success_url = reverse_lazy('core:lista_usuarios')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.get_user()
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, f"La contraseña para el usuario {self.get_user().username} ha sido cambiada exitosamente.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Cambiar Contraseña para {self.get_user().username}'
        context['usuario_a_editar'] = self.get_user()
        return context

    def get_user(self):
        return get_object_or_404(User, pk=self.kwargs['pk'])


class UsuarioListView(AdminRequiredMixin, ListView):
    model = User
    template_name = 'registration/usuario_list.html'
    context_object_name = 'usuarios'
    
    def get_queryset(self):
        return User.objects.select_related('perfilusuario').all()


@admin_required
def cambiar_rol(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        nuevo_rol = request.POST.get('rol')
        if nuevo_rol in [rol[0] for rol in PerfilUsuario.ROL_OPCIONES]:
            perfil_usuario = usuario.perfilusuario
            perfil_usuario.rol = nuevo_rol
            perfil_usuario.save()
            
            usuario.groups.clear()
            grupo_nombre = nuevo_rol.capitalize() if nuevo_rol != 'recepcionista' else 'Recepcionista'
            grupo, created = Group.objects.get_or_create(name=grupo_nombre)
            usuario.groups.add(grupo)
            
            messages.success(request, f'Rol de {usuario.username} actualizado a {nuevo_rol}.')
        else:
            messages.error(request, 'Rol no válido.')
        
        return redirect('core:lista_usuarios')
    
    context = {
        'usuario': usuario,
        'roles': PerfilUsuario.ROL_OPCIONES
    }
    return render(request, 'registration/cambiar_rol.html', context)