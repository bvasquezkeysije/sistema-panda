# Contributing Guide

## Branching Strategy
- `main`: production-ready code. Protected branch, no direct pushes.
- `develop`: integration branch for team work.
- `feature/*`: short-lived feature branches created from `develop`.
- `fix/*`: bugfix branches created from `develop`.
- `hotfix/*`: urgent fixes created from `main`, then merged back to `main` and `develop`.

## Daily Workflow
1. Sync local `develop`.
2. Create a branch from `develop`:
   - `feature/<scope>-<short-name>`
   - `fix/<scope>-<short-name>`
3. Commit in small, reviewable units.
4. Push branch and open PR to `develop`.
5. Merge via squash after approval and passing checks.

## Commit Convention
Use Conventional Commits:
- `feat(inventario): agrega modal de categorias`
- `fix(auth): corrige redireccion post login`
- `chore(docker): ajusta compose para pgadmin`
- `docs(workflow): agrega guia de ramas`

Types:
- `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `build`, `ci`

## Pull Request Rules
- PR title follows commit convention.
- Include objective, scope, test evidence, and risks.
- Keep PRs focused and small.
- No direct commits to `main` or `develop`.

## Branch Protection (GitHub)
For `main` and `develop`:
- Require pull request before merging.
- Require at least 1 approval.
- Dismiss stale reviews on new commits.
- Require status checks to pass before merging.
- Restrict direct pushes.

