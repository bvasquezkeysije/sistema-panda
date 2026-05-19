# Arquitectura Técnica

## Contenedores

1. `panda_db`
- Motor PostgreSQL 15
- Volumen persistente: `panda_db_data`

2. `panda_backend`
- Django + Gunicorn
- Ejecuta al inicio:
  - `migrate`
  - `collectstatic`
  - `seed_demo`
- Volumen de estáticos compartido: `panda_static_data`

3. `panda_frontend`
- Nginx
- Reverse proxy hacia backend (`backend:8000`)
- Sirve estáticos desde `panda_static_data`

4. `panda_pgadmin`
- Administración DB
- Volumen persistente: `panda_pgadmin_data`

## Decisiones clave

- Separación de frontend y backend para despliegue limpio en Ubuntu.
- Seeders idempotentes para inicialización consistente en cualquier entorno.
- Migraciones en repositorio para evitar drift entre ambientes.
- Variables de entorno separadas por contexto (`.env`, `infra/.env`, `backend/.env`).

## Próximos módulos

- Auth con roles (admin, almacén, ventas).
- API REST para móvil o frontend desacoplado.
- Módulos de compras, ventas, movimientos y reportes.
