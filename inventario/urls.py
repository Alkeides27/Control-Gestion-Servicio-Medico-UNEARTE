from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    # Vista principal
    path('', views.index, name='index'),
    
    # URLs para Categorías
    path('categorias/', views.listar_categorias, name='listar_categorias'),
    path('categorias/crear/', views.crear_categoria, name='crear_categoria'),
    path('categorias/<int:categoria_id>/editar/', views.editar_categoria, name='editar_categoria'),
    path('categorias/<int:categoria_id>/eliminar/', views.eliminar_categoria, name='eliminar_categoria'),
    path('categorias/exportar/pdf/', views.exportar_categorias_pdf, name='exportar_categorias_pdf'),
    path('categorias/exportar/excel/', views.exportar_categorias_excel, name='exportar_categorias_excel'),
    
    # URLs para Proveedores
    path('proveedores/', views.listar_proveedores, name='listar_proveedores'),
    path('proveedores/crear/', views.crear_proveedor, name='crear_proveedor'),
    path('proveedores/<int:proveedor_id>/editar/', views.editar_proveedor, name='editar_proveedor'),
    path('proveedores/<int:proveedor_id>/eliminar/', views.eliminar_proveedor, name='eliminar_proveedor'),
    path('proveedores/exportar/pdf/', views.exportar_proveedores_pdf, name='exportar_proveedores_pdf'),
    path('proveedores/exportar/excel/', views.exportar_proveedores_excel, name='exportar_proveedores_excel'),
    
    # URLs para Medicamentos
    path('medicamentos/', views.listar_medicamentos, name='listar_medicamentos'),
    path('medicamentos/crear/', views.crear_medicamento, name='crear_medicamento'),
    path('medicamentos/<int:medicamento_id>/editar/', views.editar_medicamento, name='editar_medicamento'),
    path('medicamentos/<int:medicamento_id>/eliminar/', views.eliminar_medicamento, name='eliminar_medicamento'),
    path('medicamentos/exportar/pdf/', views.exportar_medicamentos_pdf, name='exportar_medicamentos_pdf'),
    path('medicamentos/exportar/excel/', views.exportar_medicamentos_excel, name='exportar_medicamentos_excel'),
    
    # URLs para Inventario
    path('inventario/', views.listar_inventario, name='listar_inventario'),
    path('inventario/crear/', views.crear_inventario, name='crear_inventario'),
    path('inventario/<int:inventario_id>/editar/', views.editar_inventario, name='editar_inventario'),
    path('inventario/<int:inventario_id>/eliminar/', views.eliminar_inventario, name='eliminar_inventario'),
    path('inventario/exportar/pdf/', views.exportar_inventario_pdf, name='exportar_inventario_pdf'),
    path('inventario/exportar/excel/', views.exportar_inventario_excel, name='exportar_inventario_excel'),
    
    # URLs para Stock de Medicamentos
    path('stock/', views.stock_medicamentos, name='stock_medicamentos'),
    path('stock/exportar/pdf/', views.exportar_stock_pdf, name='exportar_stock_pdf'),
    path('stock/exportar/excel/', views.exportar_stock_excel, name='exportar_stock_excel'),
    
    # URLs para Movimientos
    path('movimientos/', views.listar_movimientos, name='listar_movimientos'),
    path('movimientos/salida/', views.crear_salida_inventario, name='crear_salida_inventario'),

    # URL para AJAX
    path('ajax/crear-medicamento/', views.crear_medicamento_ajax, name='crear_medicamento_ajax'),
    path('ajax/crear-categoria/', views.crear_categoria_ajax, name='crear_categoria_ajax'),
    path('ajax/crear-proveedor/', views.crear_proveedor_ajax, name='crear_proveedor_ajax'),
]