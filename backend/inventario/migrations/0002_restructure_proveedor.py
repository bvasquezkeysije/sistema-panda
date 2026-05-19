from django.db import migrations, models
import django.db.models.deletion


def copy_old_proveedores(apps, schema_editor):
    conn = schema_editor.connection
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT id, nombre, ruc, telefono, correo, direccion, activo, created_at "
            "FROM inventario_proveedor_old"
        )
        for row in cursor.fetchall():
            old_id, nombre, ruc, telefono, correo, direccion, activo, created_at = row
            codigo = f"PROV-{old_id:03d}"

            cursor.execute(
                """INSERT INTO inventario_proveedor
                   (id_proveedor, codigo, razon_social, nombre_comercial, tipo,
                    ruc_o_taxid, pais, moneda, condicion_pago, estado, fecha_registro)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                [old_id, codigo, nombre, nombre, "NACIONAL",
                 ruc, "Perú", "PEN", "CONTADO", activo, created_at],
            )

            if telefono or correo:
                cursor.execute(
                    """INSERT INTO inventario_proveedorcontacto
                       (id_proveedor_id, nombre_contacto, cargo, telefono, email, es_principal)
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    [old_id, "Contacto principal", "VENTAS", telefono or "", correo or "", True],
                )

            if direccion:
                cursor.execute(
                    """INSERT INTO inventario_proveedordireccion
                       (id_proveedor_id, tipo, direccion_completa, ciudad)
                       VALUES (%s, %s, %s, %s)""",
                    [old_id, "FISCAL", direccion, "Chiclayo"],
                )

        cursor.execute(
            "SELECT setval('inventario_proveedor_id_proveedor_seq', "
            "COALESCE((SELECT MAX(id_proveedor) FROM inventario_proveedor), 1))"
        )
        cursor.execute(
            "SELECT setval('inventario_proveedorcontacto_id_contacto_seq', "
            "COALESCE((SELECT MAX(id_contacto) FROM inventario_proveedorcontacto), 1))"
        )
        cursor.execute(
            "SELECT setval('inventario_proveedordireccion_id_direccion_seq', "
            "COALESCE((SELECT MAX(id_direccion) FROM inventario_proveedordireccion), 1))"
        )


def reverse_copy(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("inventario", "0001_initial"),
    ]

    operations = [
        # 1. Drop existing FK constraint on Producto (DB only)
        migrations.RunSQL(
            """DO $$ DECLARE
                fk_name text;
            BEGIN
                SELECT conname INTO fk_name FROM pg_constraint
                WHERE conrelid = 'inventario_producto'::regclass
                  AND contype = 'f'
                  AND conkey = ARRAY[(SELECT attnum FROM pg_attribute
                                      WHERE attrelid = 'inventario_producto'::regclass
                                        AND attname = 'proveedor_id')];
                EXECUTE 'ALTER TABLE inventario_producto DROP CONSTRAINT ' || quote_ident(fk_name);
            END $$;""",
            "SELECT 1",
        ),
        # 2. Rename old table out of the way
        migrations.RunSQL(
            "ALTER TABLE inventario_proveedor RENAME TO inventario_proveedor_old",
            "ALTER TABLE inventario_proveedor_old RENAME TO inventario_proveedor",
        ),
        # 3. Remove old Proveedor from Django state (DB table already renamed)
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel("Proveedor"),
            ],
            database_operations=[],
        ),
        # 4. Create new Proveedor (state + DB)
        migrations.CreateModel(
            name="Proveedor",
            fields=[
                ("id_proveedor", models.BigAutoField(primary_key=True, serialize=False)),
                ("codigo", models.CharField(max_length=20, unique=True)),
                ("razon_social", models.CharField(max_length=200)),
                ("nombre_comercial", models.CharField(blank=True, max_length=200)),
                (
                    "tipo",
                    models.CharField(
                        choices=[("NACIONAL", "Nacional"), ("EXTRANJERO", "Extranjero")],
                        default="NACIONAL",
                        max_length=20,
                    ),
                ),
                ("ruc_o_taxid", models.CharField(max_length=20, unique=True)),
                ("pais", models.CharField(default="Perú", max_length=100)),
                (
                    "moneda",
                    models.CharField(
                        choices=[("PEN", "Soles"), ("USD", "Dólares")],
                        default="PEN",
                        max_length=5,
                    ),
                ),
                (
                    "condicion_pago",
                    models.CharField(
                        choices=[
                            ("CONTADO", "Contado"),
                            ("CREDITO15", "Crédito 15 días"),
                            ("CREDITO30", "Crédito 30 días"),
                            ("CREDITO60", "Crédito 60 días"),
                        ],
                        default="CONTADO",
                        max_length=20,
                    ),
                ),
                ("estado", models.BooleanField(default=True)),
                ("fecha_registro", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["razon_social"],
            },
        ),
        # 5. Create ProveedorContacto (state + DB)
        migrations.CreateModel(
            name="ProveedorContacto",
            fields=[
                ("id_contacto", models.BigAutoField(primary_key=True, serialize=False)),
                (
                    "id_proveedor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="contactos",
                        to="inventario.proveedor",
                    ),
                ),
                ("nombre_contacto", models.CharField(max_length=150)),
                (
                    "cargo",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("VENTAS", "Ventas"),
                            ("LOGISTICA", "Logística"),
                            ("GERENTE", "Gerente"),
                            ("OTROS", "Otros"),
                        ],
                        max_length=30,
                    ),
                ),
                ("telefono", models.CharField(blank=True, max_length=20)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("es_principal", models.BooleanField(default=False)),
            ],
            options={
                "verbose_name_plural": "ProveedorContactos",
            },
        ),
        # 6. Create ProveedorDireccion (state + DB)
        migrations.CreateModel(
            name="ProveedorDireccion",
            fields=[
                ("id_direccion", models.BigAutoField(primary_key=True, serialize=False)),
                (
                    "id_proveedor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="direcciones",
                        to="inventario.proveedor",
                    ),
                ),
                (
                    "tipo",
                    models.CharField(
                        choices=[
                            ("FISCAL", "Fiscal"),
                            ("ALMACEN", "Almacén"),
                            ("SUCURSAL", "Sucursal"),
                        ],
                        default="FISCAL",
                        max_length=20,
                    ),
                ),
                ("direccion_completa", models.CharField(max_length=300)),
                ("ciudad", models.CharField(default="Chiclayo", max_length=100)),
            ],
            options={
                "verbose_name_plural": "ProveedorDirecciones",
            },
        ),
        # 7. Copy data from old table to new tables (new table has data before FK is added)
        migrations.RunPython(copy_old_proveedores, reverse_copy),
        # 8. Add FK constraint back (DB only) — data now exists in new tables
        migrations.RunSQL(
            "ALTER TABLE inventario_producto ADD CONSTRAINT "
            "inventario_producto_proveedor_id_fkey "
            "FOREIGN KEY (proveedor_id) REFERENCES inventario_proveedor(id_proveedor) "
            "ON DELETE RESTRICT",
            "SELECT 1",
        ),
        # 9. Restore FK on Producto in Django state (column already exists)
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name="producto",
                    name="proveedor",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="productos",
                        to="inventario.proveedor",
                    ),
                ),
            ],
            database_operations=[],
        ),
        # 10. Drop old table
        migrations.RunSQL(
            "DROP TABLE inventario_proveedor_old",
            "SELECT 1",
        ),
    ]
