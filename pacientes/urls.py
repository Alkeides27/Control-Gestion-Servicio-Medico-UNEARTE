from django.urls import path
from . import views

app_name = 'pacientes'

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create, name='create'),
    path('<int:paciente_id>/', views.show, name='show'),
    path('<int:paciente_id>/edit/', views.edit, name='edit'),
    path('<int:paciente_id>/destroy/', views.destroy, name='destroy'),
    path('search/', views.search, name='search'),
    # URLs AJAX para cargar datos dinámicamente
    path('ajax/cargar-estados/', views.cargar_estados, name='cargar_estados'),
    path('ajax/cargar-ciudades/', views.cargar_ciudades, name='cargar_ciudades'),
    path('ajax/crear-tipo-telefono/', views.crear_tipo_telefono_ajax, name='crear_tipo_telefono_ajax'),

    # URLs de Exportación
    path('exportar/pdf/', views.exportar_pacientes_pdf, name='exportar_pacientes_pdf'),
    path('exportar/excel/', views.exportar_pacientes_excel, name='exportar_pacientes_excel'),
]