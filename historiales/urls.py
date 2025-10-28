from django.urls import path
from .views import (
    HistorialMedicoListView, HistorialMedicoCreateView, HistorialMedicoDetailView,
    HistorialMedicoUpdateView, HistorialMedicoDeleteView,
    JustificativoCreateView, ReferenciaCreateView, ReposoCreateView, RecipeCreateView,
    JustificativoDeleteView, ReferenciaDeleteView, ReposoDeleteView, RecipeDeleteView, # Vistas de borrado
    search,
    generar_recipe_pdf,
    generar_reposo_pdf,
    generar_justificativo_pdf,
    generar_referencia_pdf,
    generar_historia_general_pdf,
) 

app_name = 'historiales'

urlpatterns = [
    path('', HistorialMedicoListView.as_view(), name='index'),
    # Mantenemos la URL de creación simple, el paciente se pasa por GET (?paciente_id=X)
    path('crear/', HistorialMedicoCreateView.as_view(), name='create'),
    path('<int:pk>/', HistorialMedicoDetailView.as_view(), name='show'),
    path('<int:pk>/editar/', HistorialMedicoUpdateView.as_view(), name='edit'),
    path('<int:pk>/eliminar/', HistorialMedicoDeleteView.as_view(), name='destroy'),
    path('search/', search, name='search'),

    # --- URLs para crear documentos asociados a un historial ---
    path('<int:historial_pk>/documentos/justificativo/crear/', JustificativoCreateView.as_view(), name='justificativo_create'),
    path('<int:historial_pk>/documentos/referencia/crear/', ReferenciaCreateView.as_view(), name='referencia_create'),
    path('<int:historial_pk>/documentos/reposo/crear/', ReposoCreateView.as_view(), name='reposo_create'),
    path('<int:historial_pk>/documentos/recipe/crear/', RecipeCreateView.as_view(), name='recipe_create'),

    # --- URLs para generar PDFs ---
    path('documentos/recipe/<int:recipe_pk>/pdf/', generar_recipe_pdf, name='recipe_pdf'),
    path('documentos/reposo/<int:reposo_pk>/pdf/', generar_reposo_pdf, name='reposo_pdf'),
    path('documentos/justificativo/<int:justificativo_pk>/pdf/', generar_justificativo_pdf, name='justificativo_pdf'),
    path('documentos/referencia/<int:referencia_pk>/pdf/', generar_referencia_pdf, name='referencia_pdf'),
    path('historia-general/<int:historia_pk>/pdf/', generar_historia_general_pdf, name='historia_general_pdf'),
]