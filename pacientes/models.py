from django.db import models
from django.core.exceptions import ValidationError

class TipoDocumento(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'tipos_documento'
        verbose_name = 'Tipo de Documento'
        verbose_name_plural = 'Tipos de Documento'

class Genero(models.TextChoices):
    MASCULINO = 'M', 'Masculino'
    FEMENINO = 'F', 'Femenino'

class Pais(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    codigo_iso = models.CharField(max_length=3, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'paises'
        verbose_name = 'País'
        verbose_name_plural = 'Países'

class Estado(models.Model):
    nombre = models.CharField(max_length=100)
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre}, {self.pais.nombre}"

    class Meta:
        db_table = 'estados'
        unique_together = ('nombre', 'pais')
        verbose_name = 'Estado'
        verbose_name_plural = 'Estados'

class Ciudad(models.Model):
    nombre = models.CharField(max_length=100)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre}, {self.estado.nombre}"

    class Meta:
        db_table = 'ciudades'
        unique_together = ('nombre', 'estado')
        verbose_name = 'Ciudad'
        verbose_name_plural = 'Ciudades'

class TipoTelefono(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    mascara = models.CharField(max_length=20, blank=True, null=True)  # Ej: (XXX) XXX-XXXX
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'tipos_telefono'
        verbose_name = 'Tipo de Teléfono'
        verbose_name_plural = 'Tipos de Teléfono'

class Paciente(models.Model):
    # Documento fijo a Cédula de Identidad Venezolana (8 caracteres máximo)
    numero_documento = models.CharField(max_length=8, unique=True)
    nombre = models.CharField(max_length=255)
    apellido = models.CharField(max_length=255)
    fecha_nacimiento = models.DateField()
    genero = models.CharField(
        max_length=1,
        choices=Genero.choices,
        default=Genero.MASCULINO
    )
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    @property
    def edad(self):
        from datetime import date
        today = date.today()
        return today.year - self.fecha_nacimiento.year - (
            (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )

    class Meta:
        db_table = 'pacientes'
        indexes = [
            models.Index(fields=['apellido', 'nombre']),
            models.Index(fields=['fecha_nacimiento']),
        ]
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'

class Direccion(models.Model):
    paciente = models.OneToOneField(Paciente, on_delete=models.CASCADE, related_name='direccion')
    ciudad = models.ForeignKey(Ciudad, on_delete=models.CASCADE)
    direccion = models.CharField(max_length=255)
    codigo_postal = models.CharField(max_length=4, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.direccion}, {self.ciudad}"

    def clean(self):
        # Validar que si hay ciudad (aunque sea fija), debe haber dirección
        if self.ciudad_id and not self.direccion:
             raise ValidationError("Debe ingresar una dirección cuando selecciona una ciudad.")

    def save(self, *args, **kwargs):
        # Llamar a la validación antes de guardar
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'direcciones'
        verbose_name = 'Dirección'
        verbose_name_plural = 'Direcciones'

class Telefono(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='telefonos')
    tipo_telefono = models.ForeignKey(TipoTelefono, on_delete=models.CASCADE)
    numero = models.CharField(max_length=11)
    es_principal = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.numero} ({self.tipo_telefono.nombre})"

    class Meta:
        db_table = 'telefonos'
        unique_together = ('paciente', 'numero')
        verbose_name = 'Teléfono'
        verbose_name_plural = 'Teléfonos'
