from django.contrib import admin
from .models import Categoria, MovimientoStock, Producto, Proveedor, ProveedorContacto, ProveedorDireccion


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "activa", "created_at")
    search_fields = ("nombre",)
    list_filter = ("activa",)


class ProveedorContactoInline(admin.TabularInline):
    model = ProveedorContacto
    extra = 1


class ProveedorDireccionInline(admin.TabularInline):
    model = ProveedorDireccion
    extra = 1


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ("codigo", "razon_social", "tipo", "ruc_o_taxid", "pais", "estado")
    search_fields = ("codigo", "razon_social", "ruc_o_taxid")
    list_filter = ("tipo", "estado", "pais")
    inlines = [ProveedorContactoInline, ProveedorDireccionInline]


@admin.register(ProveedorContacto)
class ProveedorContactoAdmin(admin.ModelAdmin):
    list_display = ("nombre_contacto", "id_proveedor", "cargo", "telefono", "email", "es_principal")
    search_fields = ("nombre_contacto", "email")
    list_filter = ("cargo", "es_principal")


@admin.register(ProveedorDireccion)
class ProveedorDireccionAdmin(admin.ModelAdmin):
    list_display = ("id_proveedor", "tipo", "ciudad", "direccion_completa")
    search_fields = ("ciudad", "direccion_completa")
    list_filter = ("tipo", "ciudad")


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "categoria", "proveedor", "precio_venta", "stock_actual", "activo")
    search_fields = ("codigo", "nombre")
    list_filter = ("categoria", "activo")


@admin.register(MovimientoStock)
class MovimientoStockAdmin(admin.ModelAdmin):
    list_display = ("fecha", "producto", "tipo", "cantidad", "referencia")
    search_fields = ("producto__codigo", "producto__nombre", "referencia")
    list_filter = ("tipo",)
