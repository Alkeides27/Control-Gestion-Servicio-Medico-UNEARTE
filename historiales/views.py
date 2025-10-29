# En historiales/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, UpdateView, DetailView, ListView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction # Importante para guardar múltiples formularios
from django.http import HttpResponseForbidden

from .models import (
    HistorialMedico, HistoriaGeneral, HistoriaNutricion,
    DocumentoJustificativo, DocumentoReferencia, DocumentoReposo, DocumentoRecipe
)
from .forms import (
    HistorialMedicoForm, HistoriaGeneralForm, HistoriaNutricionForm,
    DocumentoJustificativoForm, DocumentoReferenciaForm, DocumentoReposoForm, DocumentoRecipeForm
)
from pacientes.models import Paciente, Telefono
from core.decorators import medico_required # Asegúrate de tener los decoradores
from django.utils.decorators import method_decorator

# --- Vista de Creación ---
@method_decorator(medico_required, name='dispatch')
class HistorialMedicoCreateView(LoginRequiredMixin, CreateView):
    model = HistorialMedico
    form_class = HistorialMedicoForm # Formulario del contenedor
    template_name = 'historiales/create_edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paciente_id = self.request.GET.get('paciente_id')
        paciente = None
        creating_patient = not bool(paciente_id) # True si no hay paciente_id
        medico = self.request.user

        if paciente_id:
            paciente = get_object_or_404(Paciente, pk=paciente_id)
            context['paciente'] = paciente
            context['titulo'] = f"Crear Nuevo Historial para {paciente}"
        else:
            context['titulo'] = "Crear Nuevo Historial y Paciente"

        # Inicializar formularios secundarios
        form_kwargs = {'prefix': 'general', 'paciente': paciente, 'medico': medico, 'create_patient': creating_patient}
        if self.request.POST:
            context['general_form'] = HistoriaGeneralForm(self.request.POST, **form_kwargs)
        else:
            context['general_form'] = HistoriaGeneralForm(**form_kwargs)
            
        context['creating_patient'] = creating_patient
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        general_form = context['general_form']
        creating_patient = context['creating_patient']
        paciente = context.get('paciente')

        if not general_form.is_valid():
            print("Errores General:", general_form.errors)
            form.add_error(None, "Por favor corrija los errores en el formulario de Historia General.")
            return self.form_invalid(form)

        with transaction.atomic():
            if creating_patient:
                try:
                    paciente = Paciente.objects.create(
                        numero_documento=general_form.cleaned_data['create_cedula'],
                        nombre=general_form.cleaned_data['create_nombre'],
                        apellido=general_form.cleaned_data['create_apellido'],
                        genero=general_form.cleaned_data['create_genero'],
                        fecha_nacimiento=general_form.cleaned_data['create_fecha_nacimiento'],
                    )
                    Telefono.objects.create(
                        paciente=paciente,
                        numero=general_form.cleaned_data['create_telefono'],
                        es_principal=True
                    )
                except Exception as e:
                    form.add_error(None, f"Error al crear el paciente: {e}")
                    return self.form_invalid(form)

            if not paciente:
                form.add_error(None, "No se pudo determinar el paciente para este historial.")
                return self.form_invalid(form)

            historial = form.save(commit=False)
            historial.paciente = paciente
            historial.medico = self.request.user
            historial.save()

            general = general_form.save(commit=False)
            general.historial_padre = historial
            general.save()

        return redirect(self.get_success_url(historial.id)) # Redirigir al detalle

    # get_initial ya no es necesario aquí para el paciente
    
    def get_success_url(self, historial_id):
        return reverse_lazy('historiales:show', kwargs={'pk': historial_id})

# --- HistorialMedicoUpdateView ---
# Asegúrate de que también pasa 'paciente' y 'medico' al inicializar HistoriaGeneralForm
@method_decorator(medico_required, name='dispatch')
class HistorialMedicoUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = HistorialMedico
    form_class = HistorialMedicoForm
    template_name = 'historiales/create_edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        historial = self.get_object()
        paciente = historial.paciente
        medico = historial.medico
        context['paciente'] = paciente
        
        # Siempre pasamos create_patient=False en edición
        form_kwargs = {'prefix': 'general', 'paciente': paciente, 'medico': medico, 'create_patient': False}

        if self.request.POST:
            context['general_form'] = HistoriaGeneralForm(self.request.POST, instance=getattr(historial, 'historia_general', None), **form_kwargs)
        else:
            context['general_form'] = HistoriaGeneralForm(instance=getattr(historial, 'historia_general', None), **form_kwargs)
            
        context['titulo'] = f"Editar Historia General de {paciente}"
        # No estamos creando paciente en modo edición
        context['creating_patient'] = False
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        general_form = context['general_form']

        if general_form.is_valid():
            with transaction.atomic():
                form.save()
                general_form.save()
            return redirect(self.get_success_url())
        else:
            print("Errores General:", general_form.errors) # DEBUG
            return self.form_invalid(form)

    def test_func(self):

        historial = self.get_object()

        return hasattr(self.request.user, 'perfilusuario') and self.request.user.perfilusuario.rol == 'admin' or historial.medico == self.request.user
    def get_success_url(self):
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
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().select_related('paciente', 'medico').order_by('-fecha')
        filtro = self.request.GET.get('filtro', 'todos')

        if filtro == 'mios':
            return queryset.filter(medico=self.request.user)
        
        return queryset # Por defecto, muestra todos

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filtro_actual'] = self.request.GET.get('filtro', 'todos')
        return context

def search(request):
    query = request.GET.get('q', '')
    historiales = HistorialMedico.objects.all().order_by('-fecha')
    
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
        return hasattr(self.request.user, 'perfilusuario') and self.request.user.perfilusuario.rol == 'admin' or historial.medico == self.request.user

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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['historial'] = self.historial_padre
        kwargs['paciente'] = self.historial_padre.paciente
        return kwargs

    # Permiso: Solo el dueño del historial padre puede crear documentos
    def test_func(self):
        return hasattr(self.request.user, 'perfilusuario') and self.request.user.perfilusuario.rol == 'admin' or self.historial_padre.medico == self.request.user
        
    def form_valid(self, form):
        documento = form.save(commit=False)
        documento.historial_padre = self.historial_padre
        documento.save()
        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['historial'] = self.historial_padre
        context['paciente'] = self.historial_padre.paciente
        context['titulo'] = f"Crear {self.model._meta.verbose_name} para {self.historial_padre.paciente}"
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

# ... (código existente) ...

class RecipeCreateView(DocumentoCreateViewBase):
    model = DocumentoRecipe
    form_class = DocumentoRecipeForm

# --- VISTAS PARA ELIMINAR LOS DOCUMENTOS ---
@method_decorator(medico_required, name='dispatch')
class DocumentoDeleteViewBase(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    template_name = 'historiales/documentos/documento_confirm_delete.html'

    def get_object(self, queryset=None):
        # Usamos el pk del documento de la URL
        return get_object_or_404(self.model, pk=self.kwargs['documento_pk'])

    def test_func(self):
        documento = self.get_object()
        return hasattr(self.request.user, 'perfilusuario') and self.request.user.perfilusuario.rol == 'admin' or documento.historial_padre.medico == self.request.user

    def get_success_url(self):
        # Redirigir de vuelta al detalle del historial
        documento = self.get_object()
        return reverse_lazy('historiales:show', kwargs={'pk': documento.historial_padre.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = f"Confirmar Borrado de {self.object._meta.verbose_name.capitalize()}"
        context['documento'] = self.object
        context['historial'] = self.object.historial_padre
        return context

class JustificativoDeleteView(DocumentoDeleteViewBase):
    model = DocumentoJustificativo

class ReferenciaDeleteView(DocumentoDeleteViewBase):
    model = DocumentoReferencia

class ReposoDeleteView(DocumentoDeleteViewBase):
    model = DocumentoReposo

class RecipeDeleteView(DocumentoDeleteViewBase):
    model = DocumentoRecipe

@medico_required
def nutricion_create_or_update(request, historial_pk):
    historial = get_object_or_404(HistorialMedico, pk=historial_pk)
    if historial.medico != request.user:
        return HttpResponseForbidden()

    try:
        nutricion = historial.historia_nutricion
    except HistoriaNutricion.DoesNotExist:
        nutricion = None

    if request.method == 'POST':
        form = HistoriaNutricionForm(request.POST, instance=nutricion, paciente=historial.paciente)
        if form.is_valid():
            nutricion = form.save(commit=False)
            nutricion.historial_padre = historial
            nutricion.save()
            return redirect('historiales:show', pk=historial.pk)
    else:
        form = HistoriaNutricionForm(instance=nutricion, paciente=historial.paciente)

    return render(request, 'historiales/nutricion_form.html', {
        'form': form,
        'historial': historial,
        'paciente': historial.paciente,
        'titulo': f"Crear/Editar Nutrición para {historial.paciente}"
    })
    
# --- VISTAS PARA GENERACIÓN DE PDF ---

from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import CSS, HTML
from django.conf import settings
import os

@medico_required
def generar_recipe_pdf(request, recipe_pk):
    """
    Genera la vista en PDF de un récipe médico.
    """
    try:
        recipe = get_object_or_404(DocumentoRecipe, pk=recipe_pk)
        historial = recipe.historial_padre
        paciente = historial.paciente
        medico = historial.medico

        if not (hasattr(request.user, 'perfilusuario') and request.user.perfilusuario.rol == 'admin' or historial.medico == request.user):
            return HttpResponse("No tiene permiso para ver este documento.", status=403)

    except DocumentoRecipe.DoesNotExist:
        return HttpResponse("El récipe no existe.", status=404)

    # ... (tus paths de cintillo, unearte_logo, etc. están bien) ...
    cintillo_path = os.path.join(settings.STATICFILES_DIRS[0], 'img', 'CINTILLO-INSTITUCIONAL-PDF.png')
    unearte_logo_path = os.path.join(settings.STATICFILES_DIRS[0], 'img', 'UNEARTE-LOGO-PDF.png')
    alma_mater_logo_path = os.path.join(settings.STATICFILES_DIRS[0], 'img', 'ALMA-MATER-LOGO-PDF.png')

    context = {
        'recipe': recipe,
        'historial': historial,
        'paciente': paciente,
        'medico': medico,
        # Seguimos pasando las rutas de archivo, las usaremos con file://
        'cintillo_path': cintillo_path,
        'unearte_logo_path': unearte_logo_path,
        'alma_mater_logo_path': alma_mater_logo_path,
    }
    
    html_string = render_to_string('historiales/pdf/recipe_template.html', context, request=request)

    # CORRECCIÓN DE TAMAÑO DE PÁGINA:
    css_string = "@page { size: A5 portrait; margin: 1.5cm; }" # Cambiado a portrait
    
    # Generar el PDF
    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf(stylesheets=[CSS(string=css_string)])

    # ... (el resto de la vista está bien) ...
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="recipe_{paciente.numero_documento}_{historial.fecha.strftime("%Y-%m-%d")}.pdf"'
    
    return response

### HISTORIA NUTRICIÓN ###
@medico_required
def generar_nutricion_pdf(request, historia_nutricion_pk):
    """
    Genera la vista en PDF de una historia de nutrición.
    """
    try:
        historia_nutricion = get_object_or_404(HistoriaNutricion, pk=historia_nutricion_pk)
        historial = historia_nutricion.historial_padre
        paciente = historial.paciente
        medico = historial.medico

        if not (hasattr(request.user, 'perfilusuario') and request.user.perfilusuario.rol == 'admin' or historial.medico == request.user):
            return HttpResponse("No tiene permiso para ver este documento.", status=403)
    except HistoriaNutricion.DoesNotExist:
        return HttpResponse("La historia de nutrición no existe.", status=404)

    # Definimos las rutas a las imágenes (usando el mismo patrón que recipe)
    cintillo_path = os.path.join(settings.STATICFILES_DIRS[0], 'img', 'CINTILLO-INSTITUCIONAL-PDF.png')
    unearte_logo_path = os.path.join(settings.STATICFILES_DIRS[0], 'img', 'UNEARTE-LOGO-PDF.png')
    alma_mater_logo_path = os.path.join(settings.STATICFILES_DIRS[0], 'img', 'ALMA-MATER-LOGO-PDF.png')

    context = {
        'documento': historia_nutricion,
        'historial': historial,
        'paciente': paciente,
        'medico': medico,
        'cintillo_path': cintillo_path,
        'unearte_logo_path': unearte_logo_path,
        'alma_mater_logo_path': alma_mater_logo_path,
    }
    
    html_string = render_to_string('historiales/pdf/nutricion_template.html', context, request=request)
    
    # CORRECCIÓN DE TAMAÑO DE PÁGINA:
    css_string = "@page { size: A4 portrait; margin: 1.5cm; }"
    
    # Generar el PDF
    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf(stylesheets=[CSS(string=css_string)])

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="nutricion_{paciente.numero_documento}_{historial.fecha.strftime("%Y-%m-%d")}.pdf"'
    
    return response

### REPOSO ###
@medico_required
def generar_reposo_pdf(request, reposo_pk):
    try:
        reposo = get_object_or_404(DocumentoReposo, pk=reposo_pk)
        historial = reposo.historial_padre
        paciente = historial.paciente
        medico = historial.medico
        if not (hasattr(request.user, 'perfilusuario') and request.user.perfilusuario.rol == 'admin' or historial.medico == request.user):
            return HttpResponse("No tiene permiso para ver este documento.", status=403)
    except DocumentoReposo.DoesNotExist:
        return HttpResponse("El reposo no existe.", status=404)

    cintillo_path = os.path.join(settings.STATICFILES_DIRS[0], 'img', 'CINTILLO-INSTITUCIONAL-PDF.png')
    unearte_logo_path = os.path.join(settings.STATICFILES_DIRS[0], 'img', 'UNEARTE-LOGO-PDF.png')
    alma_mater_logo_path = os.path.join(settings.STATICFILES_DIRS[0], 'img', 'ALMA-MATER-LOGO-PDF.png')

    context = {
        'documento': reposo,
        'historial': historial,
        'paciente': paciente,
        'medico': medico,
        'cintillo_path': cintillo_path,
        'unearte_logo_path': unearte_logo_path,
        'alma_mater_logo_path': alma_mater_logo_path,
    }
    html_string = render_to_string('historiales/pdf/reposo_template.html', context, request=request)
    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reposo_{paciente.numero_documento}_{historial.fecha.strftime("%Y-%m-%d")}.pdf"'
    return response

### JUSTIFICATIVO ###
@medico_required
def generar_justificativo_pdf(request, justificativo_pk):
    try:
        justificativo = get_object_or_404(DocumentoJustificativo, pk=justificativo_pk)
        historial = justificativo.historial_padre
        paciente = historial.paciente
        medico = historial.medico
        if not (hasattr(request.user, 'perfilusuario') and request.user.perfilusuario.rol == 'admin' or historial.medico == request.user):
            return HttpResponse("No tiene permiso para ver este documento.", status=403)
    except DocumentoJustificativo.DoesNotExist:
        return HttpResponse("El justificativo no existe.", status=404)

    cintillo_path = os.path.join(settings.STATICFILES_DIRS[0], 'img', 'CINTILLO-INSTITUCIONAL-PDF.png')
    unearte_logo_path = os.path.join(settings.STATICFILES_DIRS[0], 'img', 'UNEARTE-LOGO-PDF.png')
    alma_mater_logo_path = os.path.join(settings.STATICFILES_DIRS[0], 'img', 'ALMA-MATER-LOGO-PDF.png')

    context = {
        'documento': justificativo,
        'historial': historial,
        'paciente': paciente,
        'medico': medico,
        'cintillo_path': cintillo_path,
        'unearte_logo_path': unearte_logo_path,
        'alma_mater_logo_path': alma_mater_logo_path,
    }
    html_string = render_to_string('historiales/pdf/justificativo_template.html', context, request=request)
    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="justificativo_{paciente.numero_documento}_{historial.fecha.strftime("%Y-%m-%d")}.pdf"'
    return response

### REFERENCIA ###
@medico_required
def generar_referencia_pdf(request, referencia_pk):
    try:
        referencia = get_object_or_404(DocumentoReferencia, pk=referencia_pk)
        historial = referencia.historial_padre
        paciente = historial.paciente
        medico = historial.medico
        if not (hasattr(request.user, 'perfilusuario') and request.user.perfilusuario.rol == 'admin' or historial.medico == request.user):
            return HttpResponse("No tiene permiso para ver este documento.", status=403)
    except DocumentoReferencia.DoesNotExist:
        return HttpResponse("La referencia no existe.", status=404)

    cintillo_path = os.path.join(settings.STATICFILES_DIRS[0], 'img', 'CINTILLO-INSTITUCIONAL-PDF.png')
    unearte_logo_path = os.path.join(settings.STATICFILES_DIRS[0], 'img', 'UNEARTE-LOGO-PDF.png')
    alma_mater_logo_path = os.path.join(settings.STATICFILES_DIRS[0], 'img', 'ALMA-MATER-LOGO-PDF.png')

    context = {
        'documento': referencia,
        'historial': historial,
        'paciente': paciente,
        'medico': medico,
        'cintillo_path': cintillo_path,
        'unearte_logo_path': unearte_logo_path,
        'alma_mater_logo_path': alma_mater_logo_path,
    }
    html_string = render_to_string('historiales/pdf/referencia_template.html', context, request=request)
    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="referencia_{paciente.numero_documento}_{historial.fecha.strftime("%Y-%m-%d")}.pdf"'
    return response

### HISTORIA GENERAL ###
@medico_required
def generar_historia_general_pdf(request, historia_pk):
    try:
        historia_general = get_object_or_404(HistoriaGeneral, pk=historia_pk)
        historial = historia_general.historial_padre
        paciente = historial.paciente
        medico = historial.medico
        if historial.medico != request.user:
            return HttpResponse("No tiene permiso para ver este documento.", status=403)
    except HistoriaGeneral.DoesNotExist:
        return HttpResponse("La historia general no existe.", status=404)

    logo_path = os.path.join(settings.STATICFILES_DIRS[0], 'img', 'logo.png')
    context = {
        'documento': historia_general,
        'historial': historial,
        'paciente': paciente,
        'medico': medico,
        'logo_path': logo_path,
    }
    html_string = render_to_string('historiales/pdf/historia_general_template.html', context, request=request)
    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="historia_general_{paciente.numero_documento}_{historial.fecha.strftime("%Y-%m-%d")}.pdf"'
    return response



    
# Añadir vistas de Update y Delete para los documentos si es necesario...