from django.contrib import admin
from django.urls import path
from core.views import (
    create_or_update_category_view,
    create_product_view,
    create_proveedor_view,
    deactivate_category_view,
    deactivate_product_view,
    deactivate_proveedor_view,
    delete_proveedor_contacto_view,
    detalle_proveedor_view,
    home_view,
    list_proveedores_view,
    login_view,
    logout_view,
    save_proveedor_contacto_view,
    update_product_view,
    update_proveedor_view,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home_view, name="home"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("inventario/productos/crear/", create_product_view, name="inventario_producto_crear"),
    path("inventario/productos/<int:product_id>/editar/", update_product_view, name="inventario_producto_editar"),
    path("inventario/productos/<int:product_id>/desactivar/", deactivate_product_view, name="inventario_producto_desactivar"),
    path("inventario/categorias/guardar/", create_or_update_category_view, name="inventario_categoria_guardar"),
    path("inventario/categorias/<int:category_id>/desactivar/", deactivate_category_view, name="inventario_categoria_desactivar"),
    # Proveedores
    path("proveedores/", list_proveedores_view, name="proveedores_listar"),
    path("proveedores/<int:proveedor_id>/", detalle_proveedor_view, name="proveedores_detalle"),
    path("proveedores/crear/", create_proveedor_view, name="proveedores_crear"),
    path("proveedores/<int:proveedor_id>/editar/", update_proveedor_view, name="proveedores_editar"),
    path("proveedores/<int:proveedor_id>/desactivar/", deactivate_proveedor_view, name="proveedores_desactivar"),
    path("proveedores/<int:proveedor_id>/contactos/guardar/", save_proveedor_contacto_view, name="proveedores_contacto_guardar"),
    path("proveedores/<int:proveedor_id>/contactos/<int:contacto_id>/eliminar/", delete_proveedor_contacto_view, name="proveedores_contacto_eliminar"),
]
