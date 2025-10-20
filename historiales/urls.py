from django.urls import path
from . import views

app_name = 'historiales'

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create, name='create'),
    path('<int:historial_id>/', views.show, name='show'),
    path('<int:historial_id>/edit/', views.edit, name='edit'),
    path('<int:historial_id>/destroy/', views.destroy, name='destroy'),
    path('search/', views.search, name='search'),
    # URLs de Exportación
    path('<int:historial_id>/exportar/pdf/', views.exportar_historial_individual_pdf, name='exportar_historial_individual_pdf'),
    path('exportar/pdf/', views.exportar_historiales_pdf, name='exportar_historiales_pdf'),
    path('exportar/excel/', views.exportar_historiales_excel, name='exportar_historiales_excel'),
    # URLs para AJAX
    path('ajax/crear-alergia/', views.crear_alergia_ajax, name='crear_alergia_ajax'),
    path('ajax/crear-enfermedad/', views.crear_enfermedad_ajax, name='crear_enfermedad_ajax'),
]