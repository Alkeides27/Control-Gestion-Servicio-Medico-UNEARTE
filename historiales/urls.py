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
    nutricion_create_or_update,
)

app_name = 'historiales'

urlpatterns = [
    path('', HistorialMedicoListView.as_view(), name='index'),
    path('crear/', HistorialMedicoCreateView.as_view(), name='create'),
    path('<int:pk>/', HistorialMedicoDetailView.as_view(), name='show'),
    path('<int:pk>/editar/', HistorialMedicoUpdateView.as_view(), name='edit'),
    path('<int:pk>/eliminar/', HistorialMedicoDeleteView.as_view(), name='destroy'),
    path('search/', search, name='search'),

    # --- URLs para documentos ---
    path('<int:historial_pk>/documentos/justificativo/crear/', JustificativoCreateView.as_view(), name='justificativo_create'),
    path('documentos/justificativo/<int:documento_pk>/eliminar/', JustificativoDeleteView.as_view(), name='justificativo_delete'),

    path('<int:historial_pk>/documentos/referencia/crear/', ReferenciaCreateView.as_view(), name='referencia_create'),
    path('documentos/referencia/<int:documento_pk>/eliminar/', ReferenciaDeleteView.as_view(), name='referencia_delete'),

    path('<int:historial_pk>/documentos/reposo/crear/', ReposoCreateView.as_view(), name='reposo_create'),
    path('documentos/reposo/<int:documento_pk>/eliminar/', ReposoDeleteView.as_view(), name='reposo_delete'),

    path('<int:historial_pk>/documentos/recipe/crear/', RecipeCreateView.as_view(), name='recipe_create'),
    path('documentos/recipe/<int:documento_pk>/eliminar/', RecipeDeleteView.as_view(), name='recipe_delete'),

    # --- URL para Nutrición ---
    path('<int:historial_pk>/nutricion/', nutricion_create_or_update, name='nutricion_form'),

    # --- URLs para generar PDFs ---
    path('documentos/recipe/<int:recipe_pk>/pdf/', generar_recipe_pdf, name='recipe_pdf'),
    path('documentos/reposo/<int:reposo_pk>/pdf/', generar_reposo_pdf, name='reposo_pdf'),
    path('documentos/justificativo/<int:justificativo_pk>/pdf/', generar_justificativo_pdf, name='justificativo_pdf'),
    path('documentos/referencia/<int:referencia_pk>/pdf/', generar_referencia_pdf, name='referencia_pdf'),
]