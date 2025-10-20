from django.urls import path
from . import views

app_name = 'citas'

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create, name='create'),
    path('<int:cita_id>/', views.show, name='show'),
    path('<int:cita_id>/edit/', views.edit, name='edit'),
    path('<int:cita_id>/destroy/', views.destroy, name='destroy'),
    path('search/', views.search, name='search'),
    path('hoy/', views.citas_hoy, name='hoy'),
    path('<int:cita_id>/estado/<int:estado_id>/', views.cambiar_estado, name='cambiar_estado'),
    
    # URLs AJAX para crear tipos, motivos y estados
    path('ajax/crear-tipo-cita/', views.crear_tipo_cita_ajax, name='crear_tipo_cita_ajax'),
    path('ajax/crear-motivo-cita/', views.crear_motivo_cita_ajax, name='crear_motivo_cita_ajax'),
    path('ajax/crear-estado-cita/', views.crear_estado_cita_ajax, name='crear_estado_cita_ajax'),
    path('ajax/cambiar-estado/', views.cambiar_estado_ajax, name='cambiar_estado_ajax'),

    # URLs de Exportación
    path('exportar/pdf/', views.exportar_citas_pdf, name='exportar_citas_pdf'),
    path('exportar/excel/', views.exportar_citas_excel, name='exportar_citas_excel'),
]