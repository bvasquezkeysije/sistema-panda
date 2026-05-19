from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from inventario.models import Categoria, Producto, Proveedor, ProveedorContacto, ProveedorDireccion


class Command(BaseCommand):
    help = "Carga datos demo realistas e idempotentes para Importaciones Panda."

    @transaction.atomic
    def handle(self, *args, **options):
        self._seed_admin()
        categorias = self._seed_categorias()
        proveedores = self._seed_proveedores()
        self._seed_productos(categorias, proveedores)
        self.stdout.write(self.style.SUCCESS("Seed demo completado correctamente."))

    def _seed_admin(self):
        User = get_user_model()
        user, _ = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@importacionespanda.com",
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
        )
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password("123")
        user.save()

    def _seed_categorias(self):
        base = [
            ("Abarrotes", "Productos de consumo masivo"),
            ("Limpieza", "Detergentes, jabones y desinfectantes"),
            ("Bebidas", "Gaseosas, jugos y energizantes"),
            ("Cuidado personal", "Higiene y aseo"),
            ("Textiles", "Ropa y artículos textiles para el hogar y uso diario"),
            ("Calzado", "Calzado para dama, caballero y niños"),
            ("Farmacia y tocador", "Productos farmacéuticos y de tocador"),
            ("Hogar y bazar", "Utensilios y artículos varios para el hogar"),
            ("Juguetería", "Juguetes y entretenimiento"),
            ("Papelería", "Útiles escolares y oficina"),
        ]
        out = {}
        for nombre, descripcion in base:
            cat, _ = Categoria.objects.get_or_create(
                nombre=nombre,
                defaults={"descripcion": descripcion, "activa": True},
            )
            out[nombre] = cat
        return out

    def _seed_proveedores(self):
        base = [
            ("Distribuidora Norte SAC", "20123456789", "987654321", "ventas@norte.pe", "NACIONAL", "Perú", "PEN", "CREDITO30"),
            ("Comercial Andina EIRL", "20654321987", "976123456", "contacto@andina.pe", "NACIONAL", "Perú", "PEN", "CREDITO15"),
            ("Mayorista Pacífico SAC", "20456789123", "965000111", "info@pacifico.pe", "NACIONAL", "Perú", "PEN", "CONTADO"),
            ("Importaciones Shanghai Ltd", "TX-8956321", "8613800112233", "ventas@shanghai.cn", "EXTRANJERO", "China", "USD", "CREDITO60"),
        ]
        out = {}
        for idx, (razon_social, ruc, telefono, correo, tipo, pais, moneda, condicion) in enumerate(base, 1):
            prv, created = Proveedor.objects.get_or_create(
                ruc_o_taxid=ruc,
                defaults={
                    "codigo": f"PROV-{idx:03d}",
                    "razon_social": razon_social,
                    "nombre_comercial": razon_social,
                    "tipo": tipo,
                    "pais": pais,
                    "moneda": moneda,
                    "condicion_pago": condicion,
                    "estado": True,
                },
            )
            if created:
                ProveedorContacto.objects.create(
                    id_proveedor=prv,
                    nombre_contacto="Contacto principal",
                    cargo="VENTAS",
                    telefono=telefono,
                    email=correo,
                    es_principal=True,
                )
                ProveedorDireccion.objects.create(
                    id_proveedor=prv,
                    tipo="FISCAL",
                    direccion_completa="Chiclayo, Lambayeque",
                    ciudad="Chiclayo",
                )
            else:
                prv.codigo = f"PROV-{idx:03d}"
                prv.razon_social = razon_social
                prv.nombre_comercial = razon_social
                prv.tipo = tipo
                prv.pais = pais
                prv.moneda = moneda
                prv.condicion_pago = condicion
                prv.save()
            out[razon_social] = prv
        return out

    def _seed_productos(self, categorias, proveedores):
        base = [
            ("PAN-001", "Arroz Extra 5kg", "Abarrotes", "Distribuidora Norte SAC", "caja", "85.00", "96.00", 42, 12),
            ("PAN-002", "Azúcar Rubia 1kg", "Abarrotes", "Comercial Andina EIRL", "pack", "3.40", "4.20", 120, 30),
            ("PAN-003", "Detergente Limón 900g", "Limpieza", "Mayorista Pacífico SAC", "unidad", "5.30", "6.80", 65, 20),
            ("PAN-004", "Lejía 1L", "Limpieza", "Comercial Andina EIRL", "unidad", "2.80", "3.70", 90, 25),
            ("PAN-005", "Gaseosa Cola 3L", "Bebidas", "Distribuidora Norte SAC", "unidad", "7.20", "9.00", 55, 18),
            ("PAN-006", "Shampoo Familiar 750ml", "Cuidado personal", "Mayorista Pacífico SAC", "unidad", "11.00", "14.90", 34, 10),
            ("PAN-007", "Polo Básico Algodón", "Textiles", "Comercial Andina EIRL", "unidad", "12.00", "19.90", 70, 18),
            ("PAN-008", "Medias Deportivas Par", "Textiles", "Distribuidora Norte SAC", "pack", "4.20", "7.50", 95, 20),
            ("PAN-009", "Toalla Microfibra", "Textiles", "Mayorista Pacífico SAC", "unidad", "8.50", "13.90", 44, 12),
            ("PAN-010", "Zapatilla Urbana Hombre", "Calzado", "Comercial Andina EIRL", "unidad", "48.00", "75.00", 26, 8),
            ("PAN-011", "Sandalia Dama Verano", "Calzado", "Distribuidora Norte SAC", "unidad", "22.00", "35.90", 33, 10),
            ("PAN-012", "Zapato Escolar Niño", "Calzado", "Mayorista Pacífico SAC", "unidad", "39.00", "59.00", 21, 8),
            ("PAN-013", "Paracetamol 500mg x100", "Farmacia y tocador", "Distribuidora Norte SAC", "caja", "6.50", "9.90", 80, 20),
            ("PAN-014", "Alcohol 70° 500ml", "Farmacia y tocador", "Comercial Andina EIRL", "unidad", "3.10", "4.90", 102, 25),
            ("PAN-015", "Crema Dental 120g", "Farmacia y tocador", "Mayorista Pacífico SAC", "unidad", "3.80", "5.90", 88, 22),
            ("PAN-016", "Papel Higiénico 4u", "Farmacia y tocador", "Distribuidora Norte SAC", "pack", "7.40", "10.90", 76, 20),
            ("PAN-017", "Set Vajilla Melamina", "Hogar y bazar", "Comercial Andina EIRL", "unidad", "24.00", "39.00", 18, 6),
            ("PAN-018", "Taper Hermético 1.5L", "Hogar y bazar", "Mayorista Pacífico SAC", "unidad", "5.20", "8.90", 64, 16),
            ("PAN-019", "Escoba Multiuso", "Hogar y bazar", "Distribuidora Norte SAC", "unidad", "9.00", "14.00", 41, 12),
            ("PAN-020", "Muñeca Fashion", "Juguetería", "Comercial Andina EIRL", "unidad", "14.00", "22.90", 29, 8),
            ("PAN-021", "Carrito Fricción", "Juguetería", "Mayorista Pacífico SAC", "unidad", "7.20", "12.50", 47, 12),
            ("PAN-022", "Cuaderno A4 Rayado", "Papelería", "Distribuidora Norte SAC", "unidad", "2.10", "3.80", 120, 30),
            ("PAN-023", "Lapicero Azul x12", "Papelería", "Comercial Andina EIRL", "caja", "4.60", "7.20", 58, 15),
            ("PAN-024", "Resaltador Neón x6", "Papelería", "Mayorista Pacífico SAC", "pack", "6.30", "10.50", 36, 10),
        ]

        for codigo, nombre, categoria, proveedor, unidad, compra, venta, stock, minimo in base:
            Producto.objects.get_or_create(
                codigo=codigo,
                defaults={
                    "nombre": nombre,
                    "categoria": categorias[categoria],
                    "proveedor": proveedores[proveedor],
                    "descripcion": f"{nombre} - presentación comercial",
                    "unidad": unidad,
                    "precio_compra": Decimal(compra),
                    "precio_venta": Decimal(venta),
                    "stock_actual": stock,
                    "stock_minimo": minimo,
                    "activo": True,
                },
            )
