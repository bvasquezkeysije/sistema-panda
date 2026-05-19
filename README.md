# Sistema Panda

Arquitectura base profesional para **Importador Panda** con contenedores separados:

- `db`: PostgreSQL 15
- `backend`: Django (Gunicorn)
- `frontend`: Nginx (reverse proxy + estáticos)
- `pgadmin`: gestión visual de base de datos

## Estructura

```text
sistema-panda/
  backend/        # Django app + migraciones + seeders
  frontend/       # Nginx como frontend/reverse proxy
  infra/          # docker-compose y variables de despliegue
  docs/           # documentación técnica
```

## Variables de entorno

- Archivo principal: `.env`
- Para docker compose en Ubuntu: `infra/.env`
- Para desarrollo local backend: `backend/.env`

## Levantar en Docker (Ubuntu o Windows con Docker Desktop)

```bash
cd infra
docker compose up -d --build
```

Accesos:

- Frontend: `http://localhost:8080`
- PgAdmin: `http://localhost:8081`
- Admin Django (vía frontend): `http://localhost:8080/admin/`

## Credenciales demo iniciales

- Usuario Django: `admin`
- Contraseña Django: `admin123`
- PgAdmin: definidos en `.env`

## Migraciones y seeders

Las migraciones están versionadas en `backend/inventario/migrations/`.

Seeder idempotente:

```bash
cd backend
python manage.py seed_demo
```

Este comando crea/actualiza:

- Usuario admin demo
- Categorías
- Proveedores
- Productos realistas para inventario

## Flujo recomendado de cambios

1. Crear/editar modelos.
2. Ejecutar `python manage.py makemigrations`.
3. Ejecutar `python manage.py migrate`.
4. Actualizar seeder si aplica.
5. Probar en local y en contenedores.
