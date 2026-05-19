from django.db import models


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    activa = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name_plural = "Categorias"

    def __str__(self):
        return self.nombre


class Proveedor(models.Model):
    TIPO_CHOICES = [
        ("NACIONAL", "Nacional"),
        ("EXTRANJERO", "Extranjero"),
    ]
    MONEDA_CHOICES = [
        ("PEN", "Soles"),
        ("USD", "Dólares"),
    ]
    CONDICION_PAGO_CHOICES = [
        ("CONTADO", "Contado"),
        ("CREDITO15", "Crédito 15 días"),
        ("CREDITO30", "Crédito 30 días"),
        ("CREDITO60", "Crédito 60 días"),
    ]

    id_proveedor = models.BigAutoField(primary_key=True)
    codigo = models.CharField(max_length=20, unique=True)
    razon_social = models.CharField(max_length=200)
    nombre_comercial = models.CharField(max_length=200, blank=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default="NACIONAL")
    ruc_o_taxid = models.CharField(max_length=20, unique=True)
    pais = models.CharField(max_length=100, default="Perú")
    moneda = models.CharField(max_length=5, choices=MONEDA_CHOICES, default="PEN")
    condicion_pago = models.CharField(max_length=20, choices=CONDICION_PAGO_CHOICES, default="CONTADO")
    estado = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["razon_social"]

    def __str__(self):
        return f"{self.codigo} - {self.razon_social}"


class ProveedorContacto(models.Model):
    CARGO_CHOICES = [
        ("VENTAS", "Ventas"),
        ("LOGISTICA", "Logística"),
        ("GERENTE", "Gerente"),
        ("OTROS", "Otros"),
    ]

    id_contacto = models.BigAutoField(primary_key=True)
    id_proveedor = models.ForeignKey(
        Proveedor, on_delete=models.CASCADE, related_name="contactos"
    )
    nombre_contacto = models.CharField(max_length=150)
    cargo = models.CharField(max_length=30, choices=CARGO_CHOICES, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    es_principal = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "ProveedorContactos"

    def __str__(self):
        return f"{self.nombre_contacto} ({self.id_proveedor.codigo})"


class ProveedorDireccion(models.Model):
    TIPO_CHOICES = [
        ("FISCAL", "Fiscal"),
        ("ALMACEN", "Almacén"),
        ("SUCURSAL", "Sucursal"),
    ]

    id_direccion = models.BigAutoField(primary_key=True)
    id_proveedor = models.ForeignKey(
        Proveedor, on_delete=models.CASCADE, related_name="direcciones"
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default="FISCAL")
    direccion_completa = models.CharField(max_length=300)
    ciudad = models.CharField(max_length=100, default="Chiclayo")

    class Meta:
        verbose_name_plural = "ProveedorDirecciones"

    def __str__(self):
        return f"{self.tipo} - {self.ciudad} ({self.id_proveedor.codigo})"


class Producto(models.Model):
    UNIDAD_CHOICES = [
        ("unidad", "Unidad"),
        ("caja", "Caja"),
        ("kg", "Kilogramo"),
        ("pack", "Pack"),
    ]

    codigo = models.CharField(max_length=30, unique=True)
    nombre = models.CharField(max_length=180)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name="productos")
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name="productos")
    descripcion = models.TextField(blank=True)
    unidad = models.CharField(max_length=20, choices=UNIDAD_CHOICES, default="unidad")
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    stock_actual = models.IntegerField(default=0)
    stock_minimo = models.IntegerField(default=10)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nombre"]
        indexes = [
            models.Index(fields=["codigo"]),
            models.Index(fields=["nombre"]),
            models.Index(fields=["stock_actual"]),
        ]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class MovimientoStock(models.Model):
    TIPO_CHOICES = [
        ("ENTRADA", "Entrada"),
        ("SALIDA", "Salida"),
    ]

    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name="movimientos")
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    cantidad = models.PositiveIntegerField()
    referencia = models.CharField(max_length=80, blank=True)
    observacion = models.CharField(max_length=220, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.tipo} {self.cantidad} - {self.producto.codigo}"
