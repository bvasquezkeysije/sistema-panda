# Branching Strategy - Sistema Panda

## Branches
- `main`: stable releases only.
- `develop`: integration branch.
- `feature/*`: new functionality.
- `fix/*`: non-urgent bug fixes.
- `hotfix/*`: urgent production fixes.

## Merge Policy
- `feature/*` and `fix/*` -> `develop` via PR.
- `hotfix/*` -> `main` via PR, then back-merge to `develop`.
- Releases: `develop` -> `main` via PR.

## Naming
- `feature/inventario-filtros`
- `feature/proveedores-crud`
- `fix/login-refresh-warning`
- `hotfix/auth-failure-500`

## Review Standard
- 1 approval minimum.
- Passing checks required.
- Squash merge preferred.

