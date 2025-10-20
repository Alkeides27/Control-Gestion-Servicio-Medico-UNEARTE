from django.contrib import admin
from .models import Categoria, Proveedor, Medicamento, Inventario, MovimientoInventario

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'contacto', 'telefono', 'email')
    search_fields = ('nombre', 'contacto')

@admin.register(Medicamento)
class MedicamentoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'categoria', 'proveedor', 'precio_unitario', 'stock_minimo')
    list_filter = ('categoria', 'proveedor')
    search_fields = ('nombre', 'codigo')

@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display = ('medicamento', 'cantidad', 'fecha_caducidad', 'lote')
    list_filter = ('fecha_caducidad', 'medicamento__categoria')
    search_fields = ('medicamento__nombre', 'lote')

@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ('medicamento', 'tipo', 'cantidad', 'fecha', 'usuario')
    list_filter = ('tipo', 'fecha', 'medicamento__categoria')
    search_fields = ('medicamento__nombre', 'usuario')
    readonly_fields = ('fecha',)