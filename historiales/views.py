# En historiales/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, UpdateView, DetailView, ListView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction # Importante para guardar múltiples formularios

from .models import (
    HistorialMedico, HistoriaGeneral, HistoriaNutricion,
    DocumentoJustificativo, DocumentoReferencia, DocumentoReposo, DocumentoRecipe
)
from .forms import (
    HistorialMedicoForm, HistoriaGeneralForm, HistoriaNutricionForm,
    DocumentoJustificativoForm, DocumentoReferenciaForm, DocumentoReposoForm, DocumentoRecipeForm
)
from pacientes.models import Paciente
from core.decorators import medico_required # Asegúrate de tener los decoradores
from django.utils.decorators import method_decorator

# --- Vista de Creación ---
@method_decorator(medico_required, name='dispatch')
class HistorialMedicoCreateView(LoginRequiredMixin, CreateView):
    model = HistorialMedico
    form_class = HistorialMedicoForm # Usamos el formulario simple del contenedor
    template_name = 'historiales/create_edit.html' # CREAREMOS ESTA PLANTILLA NUEVA

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paciente_id = self.request.GET.get('paciente_id')
        paciente = None
        if paciente_id:
            paciente = get_object_or_404(Paciente, pk=paciente_id)
            context['paciente'] = paciente

        # Obtener el médico actual
        medico = self.request.user.medico if hasattr(self.request.user, 'medico') else None

        if self.request.POST:
            # Pasar paciente y médico al inicializar
            context['general_form'] = HistoriaGeneralForm(self.request.POST, prefix='general', paciente=paciente, medico=medico)
            context['nutricion_form'] = HistoriaNutricionForm(self.request.POST, prefix='nutricion') # Nutricion no necesita estos datos extra
        else:
            # Pasar paciente y médico al inicializar
            context['general_form'] = HistoriaGeneralForm(prefix='general', paciente=paciente, medico=medico)
            context['nutricion_form'] = HistoriaNutricionForm(prefix='nutricion')
        context['titulo'] = "Crear Nuevo Historial Médico"
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        # Ya tenemos paciente y medico en el contexto si todo va bien
        general_form = context['general_form']
        nutricion_form = context['nutricion_form']
        paciente = context.get('paciente')  # Obtener de contexto

        if not paciente:  # Doble chequeo por si acaso
            form.add_error(None, "No se especificó el paciente.")
            return self.form_invalid(form)

        # Validar ANTES de guardar
        is_general_valid = general_form.is_valid()
        is_nutricion_valid = nutricion_form.is_valid()

        if is_general_valid and is_nutricion_valid:
            with transaction.atomic():  # Asegura que todo se guarde o nada
                # Guardamos el contenedor principal (HistorialMedico)
                historial = form.save(commit=False)
                historial.paciente = paciente
                historial.medico = self.request.user  # Asignamos al médico logueado
                historial.save()

                # Guardamos el formato general
                general = general_form.save(commit=False)
                general.historial_padre = historial
                general.save()

                # Guardamos el formato de nutrición
                nutricion = nutricion_form.save(commit=False)
                nutricion.historial_padre = historial
                nutricion.save()

            return redirect(self.get_success_url(historial.id))  # Redirigimos al detalle del historial
        else:
            # Si algún formulario anidado no es válido
            print("Errores General:", general_form.errors)  # DEBUG
            print("Errores Nutrición:", nutricion_form.errors)  # DEBUG
            return self.form_invalid(form)

    def get_initial(self):
        initial = super().get_initial()
         # Pre-populamos el paciente si viene por GET
        paciente_id = self.request.GET.get('paciente_id')
        if paciente_id:
            initial['paciente'] = paciente_id
        return initial
        
    def get_success_url(self, historial_id):
         # Redirigir a la vista de detalle del NUEVO historial
        return reverse_lazy('historiales:show', kwargs={'pk': historial_id})

# --- Vista de Edición ---
@method_decorator(medico_required, name='dispatch')
class HistorialMedicoUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = HistorialMedico
    form_class = HistorialMedicoForm # Seguimos usando el form simple
    template_name = 'historiales/create_edit.html' # REUTILIZAMOS LA PLANTILLA

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        historial = self.get_object()
        context['paciente'] = historial.paciente # Pasamos el paciente

        if self.request.POST:
            context['general_form'] = HistoriaGeneralForm(self.request.POST, instance=historial.historia_general, prefix='general')
            context['nutricion_form'] = HistoriaNutricionForm(self.request.POST, instance=historial.historia_nutricion, prefix='nutricion')
        else:
            # Cargamos los datos existentes de los formatos relacionados
            context['general_form'] = HistoriaGeneralForm(instance=historial.historia_general, prefix='general')
            context['nutricion_form'] = HistoriaNutricionForm(instance=historial.historia_nutricion, prefix='nutricion')
        context['titulo'] = f"Editar Historial de {historial.paciente}"
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        general_form = context['general_form']
        nutricion_form = context['nutricion_form']

        if general_form.is_valid() and nutricion_form.is_valid():
            with transaction.atomic():
                # Guardamos el contenedor (no debería cambiar mucho, quizás 'updated_at')
                historial = form.save()
                # Guardamos los formatos relacionados
                general_form.save()
                nutricion_form.save()
            return redirect(self.get_success_url())
        else:
            return self.form_invalid(form)

    # Verificación de permisos: Solo el dueño puede editar
    def test_func(self):
        historial = self.get_object()
        return historial.medico == self.request.user

    def get_success_url(self):
        # Redirigir a la vista de detalle del historial que se editó
        return reverse_lazy('historiales:show', kwargs={'pk': self.object.pk})

# --- Vista de Detalle (Show) ---
# La modificaremos para mostrar los datos de los nuevos modelos
@method_decorator(medico_required, name='dispatch')
class HistorialMedicoDetailView(LoginRequiredMixin, DetailView):
    model = HistorialMedico
    template_name = 'historiales/show.html' # La plantilla actual

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        historial = self.get_object()
        context['historia_general'] = getattr(historial, 'historia_general', None)
        context['historia_nutricion'] = getattr(historial, 'historia_nutricion', None)
        # También pasamos los documentos relacionados para listarlos
        context['justificativos'] = historial.justificativos.all()
        context['referencias'] = historial.referencias.all()
        context['reposos'] = historial.reposos.all()
        context['recipes'] = historial.recipes.all()
        
        # Formularios para crear documentos (los mostraremos en modales o secciones)
        context['justificativo_form'] = DocumentoJustificativoForm(prefix='just')
        context['referencia_form'] = DocumentoReferenciaForm(prefix='ref')
        context['reposo_form'] = DocumentoReposoForm(prefix='repo')
        context['recipe_form'] = DocumentoRecipeForm(prefix='reci')

        context['titulo'] = f"Detalle Historial - {historial.paciente}"
        return context
        
# --- Vista de Lista y Borrado (ListView, DeleteView) ---
# Estas vistas probablemente no necesiten grandes cambios ahora,
# pero asegúrate de que DeleteView siga verificando los permisos (test_func).

@method_decorator(medico_required, name='dispatch')
class HistorialMedicoListView(LoginRequiredMixin, ListView):
    model = HistorialMedico
    template_name = 'historiales/index.html'
    context_object_name = 'historiales'

    def get_queryset(self):
        # Mostramos solo los historiales del médico logueado
        return HistorialMedico.objects.filter(medico=self.request.user).order_by('-fecha')

@method_decorator(medico_required, name='dispatch')
def search(request):
    query = request.GET.get('q', '')
    historiales = HistorialMedico.objects.filter(medico=request.user).order_by('-fecha')
    
    if query:
        historiales = historiales.filter(
            Q(paciente__nombre__icontains=query) |
            Q(paciente__apellido__icontains=query) |
            Q(paciente__numero_documento__icontains=query)
        ).distinct()
    
    paginator = Paginator(historiales, 10)
    page_number = request.GET.get('page')
    historiales_page = paginator.get_page(page_number)
    
    return render(request, 'historiales/search.html', {
        'historiales': historiales_page,
        'query': query
    })

@method_decorator(medico_required, name='dispatch')
class HistorialMedicoDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = HistorialMedico
    template_name = 'historiales/destroy.html'
    success_url = reverse_lazy('historiales:index')

    # Verificación de permisos: Solo el dueño puede borrar
    def test_func(self):
        historial = self.get_object()
        return historial.medico == self.request.user

# --- VISTAS PARA CREAR LOS DOCUMENTOS ---
# Necesitamos vistas separadas para manejar la creación de cada documento.
# Usaremos CreateView simples.

@method_decorator(medico_required, name='dispatch')
class DocumentoCreateViewBase(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """ Clase base para crear documentos asociados a un historial """
    template_name = 'historiales/documentos/create_form.html' # Plantilla genérica para docs
    
    def dispatch(self, request, *args, **kwargs):
         # Obtenemos el historial padre desde la URL
        self.historial_padre = get_object_or_404(HistorialMedico, pk=self.kwargs['historial_pk'])
        return super().dispatch(request, *args, **kwargs)

    # Permiso: Solo el dueño del historial padre puede crear documentos
    def test_func(self):
        return self.historial_padre.medico == self.request.user
        
    def form_valid(self, form):
        documento = form.save(commit=False)
        documento.historial_padre = self.historial_padre
        documento.save()
        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['historial'] = self.historial_padre
        context['paciente'] = self.historial_padre.paciente
        context['titulo'] = f"Crear {self.model._meta.verbose_name}"
        return context

    def get_success_url(self):
        # Volver al detalle del historial padre
        return reverse_lazy('historiales:show', kwargs={'pk': self.historial_padre.pk})

# Vistas específicas que heredan de la base
class JustificativoCreateView(DocumentoCreateViewBase):
    model = DocumentoJustificativo
    form_class = DocumentoJustificativoForm

class ReferenciaCreateView(DocumentoCreateViewBase):
    model = DocumentoReferencia
    form_class = DocumentoReferenciaForm

class ReposoCreateView(DocumentoCreateViewBase):
    model = DocumentoReposo
    form_class = DocumentoReposoForm

class RecipeCreateView(DocumentoCreateViewBase):
    model = DocumentoRecipe
    form_class = DocumentoRecipeForm
    
# Añadir vistas de Update y Delete para los documentos si es necesario...