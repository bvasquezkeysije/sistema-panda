import json

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db.models import Max
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from inventario.models import (
    Categoria,
    Producto,
    Proveedor,
    ProveedorContacto,
    ProveedorDireccion,
)


def _proveedor_to_dict(p):
    return {
        "id_proveedor": p.id_proveedor,
        "codigo": p.codigo,
        "razon_social": p.razon_social,
        "nombre_comercial": p.nombre_comercial or "",
        "tipo": p.tipo,
        "ruc_o_taxid": p.ruc_o_taxid,
        "pais": p.pais,
        "moneda": p.moneda,
        "condicion_pago": p.condicion_pago,
        "estado": p.estado,
        "fecha_registro": p.fecha_registro.isoformat() if p.fecha_registro else "",
    }


def _proveedor_detalle_dict(p):
    data = _proveedor_to_dict(p)
    data["contactos"] = [
        {
            "id_contacto": c.id_contacto,
            "nombre_contacto": c.nombre_contacto,
            "cargo": c.cargo,
            "telefono": c.telefono,
            "email": c.email,
            "es_principal": c.es_principal,
        }
        for c in p.contactos.all()
    ]
    data["direcciones"] = [
        {
            "id_direccion": d.id_direccion,
            "tipo": d.tipo,
            "direccion_completa": d.direccion_completa,
            "ciudad": d.ciudad,
        }
        for d in p.direcciones.all()
    ]
    return data


@require_http_methods(["GET"])
def home_view(request):
    context = {}
    if request.user.is_authenticated:
        productos = (
            Producto.objects.select_related("categoria", "proveedor")
            .order_by("codigo")
            .values(
                "id",
                "codigo",
                "nombre",
                "descripcion",
                "unidad",
                "categoria__nombre",
                "proveedor__id_proveedor",
                "proveedor__razon_social",
                "stock_actual",
                "stock_minimo",
                "precio_compra",
                "precio_venta",
                "activo",
            )
        )
        productos_data = [
            {
                "id": p["id"],
                "codigo": p["codigo"],
                "nombre": p["nombre"],
                "descripcion": p["descripcion"] or "",
                "unidad": p["unidad"],
                "categoria": p["categoria__nombre"],
                "proveedor_id": p["proveedor__id_proveedor"],
                "proveedor": p["proveedor__razon_social"] or "",
                "stock": p["stock_actual"],
                "stock_minimo": p["stock_minimo"],
                "precio_compra": str(p["precio_compra"]),
                "precio_venta": str(p["precio_venta"]),
                "estado": "Activo" if p["activo"] else "Inactivo",
            }
            for p in productos
        ]
        categorias = list(Categoria.objects.filter(activa=True).order_by("nombre").values_list("nombre", flat=True))
        category_data = list(
            Categoria.objects.all().order_by("nombre").values("id", "nombre", "descripcion", "activa")
        )
        counts = {}
        for p in productos:
            counts[p["categoria__nombre"]] = counts.get(p["categoria__nombre"], 0) + 1
        category_data = [
            {
                "id": c["id"],
                "nombre": c["nombre"],
                "descripcion": c["descripcion"] or "",
                "activa": c["activa"],
                "productos": counts.get(c["nombre"], 0),
            }
            for c in category_data
        ]
        proveedores = Proveedor.objects.filter(estado=True).order_by("razon_social")
        proveedores_data = [_proveedor_to_dict(p) for p in proveedores]

        context["inventory_products_json"] = json.dumps(productos_data)
        context["inventory_categories_json"] = json.dumps(categorias)
        context["inventory_category_data_json"] = json.dumps(category_data)
        context["proveedores_json"] = json.dumps(proveedores_data)
    return render(request, "home.html", context)


@require_http_methods(["GET", "POST"])
@csrf_protect
def login_view(request):
    if request.method == "GET":
        return redirect("home")
    username = request.POST.get("username", "").strip()
    password = request.POST.get("password", "")
    user = authenticate(request, username=username, password=password)
    if user is not None and user.is_active:
        login(request, user)
        return redirect("home")
    messages.error(request, "Usuario o contraseña inválidos.")
    return redirect("home")


@require_http_methods(["POST"])
@csrf_protect
def logout_view(request):
    logout(request)
    return redirect("home")


@require_http_methods(["POST"])
@csrf_protect
def create_product_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({"ok": False, "error": "No autenticado."}, status=401)
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        data = request.POST
    nombre = str(data.get("nombre", "")).strip()
    categoria_nombre = str(data.get("categoria", "")).strip()
    proveedor_id = data.get("proveedor_id")
    stock = data.get("stock", 0)
    precio_compra = data.get("precio_compra", 0)
    precio_venta = data.get("precio_venta", 0)
    if not nombre or not categoria_nombre:
        return JsonResponse({"ok": False, "error": "Nombre y categoría son obligatorios."}, status=400)
    max_num = Producto.objects.aggregate(m=Max("id"))["m"] or 0
    codigo = f"PAN-{max_num + 1:03d}"
    while Producto.objects.filter(codigo=codigo).exists():
        max_num += 1
        codigo = f"PAN-{max_num + 1:03d}"
    categoria = get_object_or_404(Categoria, nombre=categoria_nombre)
    if proveedor_id:
        proveedor = get_object_or_404(Proveedor, id_proveedor=proveedor_id)
    else:
        proveedor = Proveedor.objects.filter(estado=True).order_by("id_proveedor").first()
        if not proveedor:
            return JsonResponse({"ok": False, "error": "No hay proveedores activos."}, status=400)
    try:
        stock_int = int(stock)
        pc = float(precio_compra)
        pv = float(precio_venta)
    except ValueError:
        return JsonResponse({"ok": False, "error": "Valores numéricos inválidos."}, status=400)
    producto = Producto.objects.create(
        codigo=codigo,
        nombre=nombre,
        categoria=categoria,
        proveedor=proveedor,
        unidad="unidad",
        precio_compra=pc,
        precio_venta=pv,
        stock_actual=stock_int,
        stock_minimo=max(1, min(20, stock_int if stock_int > 0 else 10)),
        activo=True,
    )
    return JsonResponse(
        {
            "ok": True,
            "producto": {
                "id": producto.id,
                "codigo": producto.codigo,
                "nombre": producto.nombre,
                "categoria": producto.categoria.nombre,
                "stock": producto.stock_actual,
                "precio_compra": str(producto.precio_compra),
                "precio_venta": str(producto.precio_venta),
                "estado": "Activo",
            },
        }
    )


@require_http_methods(["POST"])
@csrf_protect
def update_product_view(request, product_id):
    if not request.user.is_authenticated:
        return JsonResponse({"ok": False, "error": "No autenticado."}, status=401)
    producto = get_object_or_404(Producto, id=product_id)
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        data = request.POST
    nombre = str(data.get("nombre", producto.nombre)).strip()
    categoria_nombre = str(data.get("categoria", producto.categoria.nombre)).strip()
    proveedor_id = data.get("proveedor_id", producto.proveedor_id)
    stock = data.get("stock", producto.stock_actual)
    precio_compra = data.get("precio_compra", producto.precio_compra)
    precio_venta = data.get("precio_venta", producto.precio_venta)
    if not nombre or not categoria_nombre:
        return JsonResponse({"ok": False, "error": "Nombre y categoría son obligatorios."}, status=400)
    categoria = get_object_or_404(Categoria, nombre=categoria_nombre)
    try:
        producto.nombre = nombre
        producto.categoria = categoria
        if proveedor_id:
            producto.proveedor = get_object_or_404(Proveedor, id_proveedor=proveedor_id)
        producto.stock_actual = int(stock)
        producto.precio_compra = float(precio_compra)
        producto.precio_venta = float(precio_venta)
        producto.save()
    except ValueError:
        return JsonResponse({"ok": False, "error": "Valores numéricos inválidos."}, status=400)
    return JsonResponse(
        {
            "ok": True,
            "producto": {
                "id": producto.id,
                "codigo": producto.codigo,
                "nombre": producto.nombre,
                "categoria": producto.categoria.nombre,
                "stock": producto.stock_actual,
                "precio_compra": str(producto.precio_compra),
                "precio_venta": str(producto.precio_venta),
                "estado": "Activo" if producto.activo else "Inactivo",
            },
        }
    )


@require_http_methods(["POST"])
@csrf_protect
def deactivate_product_view(request, product_id):
    if not request.user.is_authenticated:
        return JsonResponse({"ok": False, "error": "No autenticado."}, status=401)
    producto = get_object_or_404(Producto, id=product_id)
    producto.activo = False
    producto.save(update_fields=["activo"])
    return JsonResponse({"ok": True, "id": producto.id})


@require_http_methods(["POST"])
@csrf_protect
def create_or_update_category_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({"ok": False, "error": "No autenticado."}, status=401)
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        data = request.POST
    cat_id = data.get("id")
    nombre = str(data.get("nombre", "")).strip()
    descripcion = str(data.get("descripcion", "")).strip()
    if not nombre:
        return JsonResponse({"ok": False, "error": "Nombre obligatorio."}, status=400)
    if cat_id:
        categoria = get_object_or_404(Categoria, id=int(cat_id))
        if Categoria.objects.exclude(id=categoria.id).filter(nombre__iexact=nombre).exists():
            return JsonResponse({"ok": False, "error": "Ya existe una categoría con ese nombre."}, status=400)
        categoria.nombre = nombre
        categoria.descripcion = descripcion
        categoria.save()
    else:
        if Categoria.objects.filter(nombre__iexact=nombre).exists():
            return JsonResponse({"ok": False, "error": "Ya existe una categoría con ese nombre."}, status=400)
        categoria = Categoria.objects.create(nombre=nombre, descripcion=descripcion, activa=True)
    return JsonResponse(
        {
            "ok": True,
            "categoria": {
                "id": categoria.id,
                "nombre": categoria.nombre,
                "descripcion": categoria.descripcion or "",
                "activa": categoria.activa,
            },
        }
    )


@require_http_methods(["POST"])
@csrf_protect
def deactivate_category_view(request, category_id):
    if not request.user.is_authenticated:
        return JsonResponse({"ok": False, "error": "No autenticado."}, status=401)
    categoria = get_object_or_404(Categoria, id=category_id)
    categoria.activa = False
    categoria.save(update_fields=["activa"])
    return JsonResponse({"ok": True, "id": categoria.id})


# ─── Proveedores CRUD ───────────────────────────────────────────────────────


@require_http_methods(["GET"])
def list_proveedores_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({"ok": False, "error": "No autenticado."}, status=401)
    proveedores = Proveedor.objects.all().order_by("razon_social")
    data = [_proveedor_to_dict(p) for p in proveedores]
    return JsonResponse({"ok": True, "proveedores": data})


@require_http_methods(["GET"])
def detalle_proveedor_view(request, proveedor_id):
    if not request.user.is_authenticated:
        return JsonResponse({"ok": False, "error": "No autenticado."}, status=401)
    proveedor = get_object_or_404(Proveedor, id_proveedor=proveedor_id)
    return JsonResponse({"ok": True, "proveedor": _proveedor_detalle_dict(proveedor)})


@require_http_methods(["POST"])
@csrf_protect
def create_proveedor_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({"ok": False, "error": "No autenticado."}, status=401)
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        data = request.POST
    razon_social = str(data.get("razon_social", "")).strip()
    ruc_o_taxid = str(data.get("ruc_o_taxid", "")).strip()
    if not razon_social or not ruc_o_taxid:
        return JsonResponse({"ok": False, "error": "Razón social y RUC/TaxID son obligatorios."}, status=400)
    if Proveedor.objects.filter(ruc_o_taxid=ruc_o_taxid).exists():
        return JsonResponse({"ok": False, "error": "Ya existe un proveedor con ese RUC/TaxID."}, status=400)
    max_id = Proveedor.objects.aggregate(m=Max("id_proveedor"))["m"] or 0
    codigo = f"PROV-{max_id + 1:03d}"
    proveedor = Proveedor.objects.create(
        codigo=codigo,
        razon_social=razon_social,
        nombre_comercial=str(data.get("nombre_comercial", razon_social)).strip(),
        tipo=str(data.get("tipo", "NACIONAL")).strip(),
        ruc_o_taxid=ruc_o_taxid,
        pais=str(data.get("pais", "Perú")).strip(),
        moneda=str(data.get("moneda", "PEN")).strip(),
        condicion_pago=str(data.get("condicion_pago", "CONTADO")).strip(),
        estado=True,
    )
    contacto_nombre = str(data.get("contacto_nombre", "")).strip()
    if contacto_nombre:
        ProveedorContacto.objects.create(
            id_proveedor=proveedor,
            nombre_contacto=contacto_nombre,
            cargo=str(data.get("contacto_cargo", "VENTAS")).strip(),
            telefono=str(data.get("contacto_telefono", "")).strip(),
            email=str(data.get("contacto_email", "")).strip(),
            es_principal=True,
        )
    direccion = str(data.get("direccion", "")).strip()
    if direccion:
        ProveedorDireccion.objects.create(
            id_proveedor=proveedor,
            tipo="FISCAL",
            direccion_completa=direccion,
            ciudad=str(data.get("ciudad", "Chiclayo")).strip(),
        )
    return JsonResponse({"ok": True, "proveedor": _proveedor_detalle_dict(proveedor)})


@require_http_methods(["POST"])
@csrf_protect
def update_proveedor_view(request, proveedor_id):
    if not request.user.is_authenticated:
        return JsonResponse({"ok": False, "error": "No autenticado."}, status=401)
    proveedor = get_object_or_404(Proveedor, id_proveedor=proveedor_id)
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        data = request.POST
    razon_social = str(data.get("razon_social", proveedor.razon_social)).strip()
    ruc_o_taxid = str(data.get("ruc_o_taxid", proveedor.ruc_o_taxid)).strip()
    if not razon_social or not ruc_o_taxid:
        return JsonResponse({"ok": False, "error": "Razón social y RUC/TaxID son obligatorios."}, status=400)
    if Proveedor.objects.exclude(id_proveedor=proveedor.id_proveedor).filter(ruc_o_taxid=ruc_o_taxid).exists():
        return JsonResponse({"ok": False, "error": "Ya existe otro proveedor con ese RUC/TaxID."}, status=400)
    proveedor.razon_social = razon_social
    proveedor.nombre_comercial = str(data.get("nombre_comercial", proveedor.nombre_comercial)).strip()
    proveedor.tipo = str(data.get("tipo", proveedor.tipo)).strip()
    proveedor.ruc_o_taxid = ruc_o_taxid
    proveedor.pais = str(data.get("pais", proveedor.pais)).strip()
    proveedor.moneda = str(data.get("moneda", proveedor.moneda)).strip()
    proveedor.condicion_pago = str(data.get("condicion_pago", proveedor.condicion_pago)).strip()
    proveedor.save()
    return JsonResponse({"ok": True, "proveedor": _proveedor_detalle_dict(proveedor)})


@require_http_methods(["POST"])
@csrf_protect
def deactivate_proveedor_view(request, proveedor_id):
    if not request.user.is_authenticated:
        return JsonResponse({"ok": False, "error": "No autenticado."}, status=401)
    proveedor = get_object_or_404(Proveedor, id_proveedor=proveedor_id)
    proveedor.estado = False
    proveedor.save(update_fields=["estado"])
    return JsonResponse({"ok": True, "id_proveedor": proveedor.id_proveedor})


@require_http_methods(["POST"])
@csrf_protect
def save_proveedor_contacto_view(request, proveedor_id):
    if not request.user.is_authenticated:
        return JsonResponse({"ok": False, "error": "No autenticado."}, status=401)
    proveedor = get_object_or_404(Proveedor, id_proveedor=proveedor_id)
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        data = request.POST
    contacto_id = data.get("id_contacto")
    nombre_contacto = str(data.get("nombre_contacto", "")).strip()
    if not nombre_contacto:
        return JsonResponse({"ok": False, "error": "Nombre del contacto es obligatorio."}, status=400)
    if contacto_id:
        contacto = get_object_or_404(ProveedorContacto, id_contacto=contacto_id, id_proveedor=proveedor)
    else:
        contacto = ProveedorContacto(id_proveedor=proveedor)
    contacto.nombre_contacto = nombre_contacto
    contacto.cargo = str(data.get("cargo", "")).strip()
    contacto.telefono = str(data.get("telefono", "")).strip()
    contacto.email = str(data.get("email", "")).strip()
    contacto.es_principal = bool(data.get("es_principal", False))
    contacto.save()
    return JsonResponse({"ok": True, "contacto": {
        "id_contacto": contacto.id_contacto,
        "nombre_contacto": contacto.nombre_contacto,
        "cargo": contacto.cargo,
        "telefono": contacto.telefono,
        "email": contacto.email,
        "es_principal": contacto.es_principal,
    }})


@require_http_methods(["POST"])
@csrf_protect
def delete_proveedor_contacto_view(request, proveedor_id, contacto_id):
    if not request.user.is_authenticated:
        return JsonResponse({"ok": False, "error": "No autenticado."}, status=401)
    contacto = get_object_or_404(ProveedorContacto, id_contacto=contacto_id, id_proveedor=proveedor_id)
    contacto.delete()
    return JsonResponse({"ok": True})
