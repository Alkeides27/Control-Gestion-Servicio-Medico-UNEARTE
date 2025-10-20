from django.db import models
from django.db.models import Sum
from datetime import date

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        db_table = 'inventario_categorias'
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'

class Proveedor(models.Model):
    nombre = models.CharField(max_length=200)
    contacto = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        db_table = 'inventario_proveedores'
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'

class Medicamento(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    codigo = models.CharField(max_length=50, unique=True, blank=True)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    stock_minimo = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Generar código automáticamente si no se proporciona o está vacío
        if not self.codigo:
            # Contar cuántos medicamentos existen
            count = Medicamento.objects.count()
            # Generar el siguiente código
            self.codigo = f'MED-{count + 1:04d}'
            
            # Verificar que el código sea único
            while Medicamento.objects.filter(codigo=self.codigo).exists():
                count += 1
                self.codigo = f'MED-{count + 1:04d}'
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.nombre} ({self.codigo})"
    
    @property
    def stock_actual(self):
        # Calcular el stock real a partir de los movimientos de inventario
        entradas = self.movimientoinventario_set.filter(tipo='entrada').aggregate(total=Sum('cantidad'))['total'] or 0
        salidas = self.movimientoinventario_set.filter(tipo='salida').aggregate(total=Sum('cantidad'))['total'] or 0
        return entradas - salidas
    
    @property
    def estado_stock(self):
        # Determinar el estado del stock
        if self.stock_actual <= 0:
            return 'agotado'
        elif self.stock_actual <= self.stock_minimo:
            return 'bajo'
        else:
            return 'normal'
    
    class Meta:
        db_table = 'inventario_medicamentos'
        verbose_name = 'Medicamento'
        verbose_name_plural = 'Medicamentos'

class Inventario(models.Model):
    medicamento = models.ForeignKey(Medicamento, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    fecha_caducidad = models.DateField()
    lote = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.medicamento.nombre} - {self.cantidad} unidades"
    
    @property
    def estado(self):
        # Determinar el estado de esta existencia
        hoy = date.today()
        if self.fecha_caducidad < hoy:
            return 'caducado'
        elif self.cantidad <= 0:
            return 'agotado'
        elif self.cantidad <= self.medicamento.stock_minimo:
            return 'bajo_stock'
        else:
            return 'disponible'
    
    @property
    def dias_para_caducar(self):
        # Calcular días restantes para caducar
        hoy = date.today()
        if self.fecha_caducidad >= hoy:
            return (self.fecha_caducidad - hoy).days
        else:
            return 0
    
    class Meta:
        db_table = 'inventario_existencias'
        verbose_name = 'Existencia'
        verbose_name_plural = 'Existencias'

class MovimientoInventario(models.Model):
    TIPO_MOVIMIENTO = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
    ]
    
    medicamento = models.ForeignKey(Medicamento, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10, choices=TIPO_MOVIMIENTO)
    cantidad = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField(blank=True, null=True)
    usuario = models.CharField(max_length=100)  # En una implementación real, sería una ForeignKey a User
    
    def __str__(self):
        return f"{self.tipo} de {self.cantidad} {self.medicamento.nombre}"
    
    class Meta:
        db_table = 'inventario_movimientos'
        verbose_name = 'Movimiento de Inventario'
        verbose_name_plural = 'Movimientos de Inventario'