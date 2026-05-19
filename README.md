# Sistema Panda

[![Django](https://img.shields.io/badge/Django-5.x-0C4B33?logo=django&logoColor=white)](#)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql&logoColor=white)](#)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](#)
[![Branching](https://img.shields.io/badge/Workflow-main%20%7C%20develop%20%7C%20feature-blue)](docs/branching-strategy.md)

Plataforma web para **Importaciones Panda** con arquitectura separada por contenedores:
- `db`: PostgreSQL
- `backend`: Django
- `frontend`: Nginx (reverse proxy)
- `pgadmin`: administraciÃ³n visual de DB

## Preview

![Preview Sistema Panda](docs/assets/preview.svg)

## Arquitectura

```mermaid
flowchart LR
    U[Usuario] --> F[Nginx Frontend]
    F --> B[Django Backend]
    B --> D[(PostgreSQL)]
    A[PgAdmin] --> D
```

## Estructura del Proyecto

```text
sistema-panda/
  backend/        # Django app, migraciones, seeders
  frontend/       # Nginx (proxy y estÃ¡ticos)
  infra/          # Docker Compose
  docs/           # Arquitectura y flujo de ramas
  .github/        # Plantillas de PR
```

## Levantar en Local con Docker

```bash
cd infra
docker compose up -d --build
```

Accesos:
- Frontend: `http://localhost:8080`
- PgAdmin: `http://localhost:8081`
- Django admin (vÃ­a frontend): `http://localhost:8080/admin/`

## Variables de Entorno

- RaÃ­z del proyecto: `.env`
- Compose/infra: `infra/.env`
- Backend local: `backend/.env`

## Migraciones y Seeder

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
python manage.py seed_demo
```

## Flujo de Trabajo (Equipo)

```mermaid
flowchart LR
    D[develop] -->|crear| F1[feature/inventario-modulo]
    F1 -->|PR| D
    D -->|release PR| M[main]
    M -->|urgente| H[hotfix/*]
    H -->|PR| M
    H -->|back-merge| D
```

MÃ¡s detalle: [Branching Strategy](docs/branching-strategy.md) y [Contributing Guide](CONTRIBUTING.md).

## Reglas de Calidad

- No push directo a `main` ni `develop`.
- Todo cambio entra por Pull Request.
- Commits con convenciÃ³n: `feat`, `fix`, `chore`, `docs`, etc.
- PR pequeÃ±o, enfocado y con evidencia de pruebas.

## Roadmap Corto

- Inventario: CRUD completo + filtros avanzados.
- Proveedores: CRUD + contactos.
- Compras/Ventas: flujos transaccionales.
- Reportes: mÃ©tricas operativas y comerciales.


