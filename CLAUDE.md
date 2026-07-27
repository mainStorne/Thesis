# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Thesis is a serverless hosting platform for college students to deploy and test web apps in isolated
containers, with automatic teardown after a class period. It is a monorepo of two independent Python
services plus deployment/orchestration config:

- **`web/`** — user-facing service ("Websis"): FastAPI + Flet (via the `flet-easy` fork) UI, PostgreSQL
  metadata store, and the orchestration logic that builds/deploys student projects.
- **`agent/`** — a gRPC daemon that runs on each Docker Swarm host that has filesystem quotas enabled;
  it manages disk quotas and shared resources (e.g. the MySQL data directory) for students.
- **`protos/`** — the shared `.proto` contract (`quota.proto`) between `web` and `agent`. Generated stubs
  live in `web/src/grpc` and `agent/src/grpc` and must be regenerated in both places together (see below).

Each service is its own `uv` project (separate `pyproject.toml`/`uv.lock`) — run all Python commands
from inside `web/` or `agent/`, not the repo root.

## Common commands

Run from inside `web/` or `agent/` as noted.

```bash
# Install deps (per service)
uv sync --all-groups

# Run tests (per service)
uv run pytest
uv run pytest tests/test_project_service.py::test_name   # single test
uv run pytest tests/test_project_service.py               # single file

# Lint / format (ruff config lives in each service's pyproject.toml)
uv run ruff check .
uv run ruff format .

# Web: DB migrations (alembic)
cd web && uv run alembic revision --autogenerate -m "message"
cd web && uv run alembic upgrade head
# or via justfile:
just migrate

# Regenerate gRPC stubs for BOTH services after editing protos/quota.proto
just gen_grpc
```

Local settings: each service reads `src/settings.yml`, which is gitignored — copy `src/settings.example.yml`
to `src/settings.yml` and fill in values (DB credentials, `jwt_secret`, `domain`, quota paths, etc.) before
running either service locally.

### Running the stack

- Dev: `docker-compose.dev.yaml` (used with the devcontainer, see `.devcontainer/devcontainer.json`).
- Prod: `docker-compose.prod.yaml` (multi-host) or `docker-compose.prod.one-host.yaml` (single host), deployed
  via `docker stack deploy` onto Docker Swarm. `create-registry.sh` must be run once to stand up a local
  registry and pull the pinned MySQL image before building/pushing.
- Both Dockerfiles use multi-stage builds with `uv sync --no-install-project --no-editable`; `web`'s
  `alembic.sh` entrypoint runs migrations before starting uvicorn on port 80. `agent` runs as `python -m src`
  (module entry point is `agent/src/__main__.py`).
- `web/dev.Dockerfile` additionally installs the `debug` dependency group and starts under `debugpy`
  listening on `:5678`.

## Architecture

### `web/` — layered per feature: repo → service → UI/servicer

- **`main.py`** — ASGI entry point. Builds `flet_fastapi.FastAPI(...)`, wires `grpc_pool` startup/shutdown
  and `src/init.py`'s `on_init`, mounts the `uploadfile` router, and mounts the Flet `App` (from `src/app.py`)
  at `/`.
- **`src/app.py`** — root Flet app (`FletEasy`); registers pages from `src/ui/views/*` and a login guard
  (`handle_login`, checks a token in client storage) — this is the actual route table.
- **`src/api/db/`** — SQLModel table definitions (`users.py`, `resource.py`) + Alembic migrations
  (`src/api/db/alembic/`).
- **`src/api/repos/`** — one repo per external system, all instantiated as module-level singletons
  (e.g. `docker_repo`, `mysql_repo`, `traefik_repo`, `account_repo`, `security_repo`, `archive_repo`,
  `filesystem_repo`). Repos do raw I/O only.
- **`src/api/services/`** — business logic composed from repos (e.g. `project_service.py` orchestrates
  `docker_repo` + `traefik_repo` to build/deploy/delete a student project as a Swarm service).
- **`src/ui/`** — Flet presentation layer: `views/` (pages), `layouts/`, `components/` (reusable widgets).
- **`src/grpc_pool.py`** + **`src/grpc/`** — gRPC client pool and generated stubs used to call the `agent`
  service (e.g. for quota checks, shared MySQL resource creation).
- **`src/conf.py`** — holds shared runtime state such as `queue_var` (a `ContextVar` used to push
  progress/status messages, e.g. "Сервис создан", to the UI during long-running deploy operations).
- **`src/settings.py`** — `pydantic-settings-yaml`-based config (`AppSettings`), loaded from
  `src/settings.yml`. Key sections: `database` (Postgres), `mysql` (admin creds for per-student DBs),
  `sublier.session_duration` (idle-teardown window), `admin` (host admin password), `domain`
  (base hosting domain), `jwt_secret`.

**Student project deploy flow** (see `ProjectService.create_project` /
`_build_project` in `src/api/services/project_service.py`): upload archive → `docker_repo.build_project`
builds a Docker image tagged `<project>.<student-login>` → `traefik_repo.add_service` registers a Traefik
middleware → `docker_repo.create_serverless_service` deploys it as a Docker Swarm service with Traefik +
Sablier labels (Sablier scales the service to zero after `sublier.session_duration` of inactivity, and
Traefik wakes it back up on the next request) → project metadata is persisted via SQLModel.

### `agent/` — mirrors the same repo → service → servicer layering

- **`src/__main__.py`** / **`src/server.py`** — gRPC server bootstrap.
- **`src/servicers/resource_servicer.py`** — gRPC service implementation exposed to `web` (implements the
  `Quota`/`Resources` RPCs defined in `protos/quota.proto`).
- **`src/services/`** (`quota_service.py`, `resources_service.py`) — business logic.
- **`src/repos/`** (`quota_repo.py`, `filesystem_repo.py`) — reads/writes Linux filesystem disk quotas
  (requires the host to have the `quota` package and quota-enabled filesystem set up — see root README)
  and manages shared resource directories (e.g. the MySQL data dir under `students_shared_base_dir`).
- **`src/interceptors/logging_interceptor.py`** — structlog-based gRPC request logging interceptor.
- **`src/settings.py`** — `QuotaSettings` (`students_shared_base_dir`, `students_home_base_dir`) and
  `enviromnent` (`LOCAL`/`PROD`), loaded from `src/settings.yml`.

### Cross-cutting

- The `agent` container must always be scheduled on the Swarm host that actually has quota enabled
  (it manages that host's filesystem quotas directly).
- Traefik (`traefik.yml`, `dynamic.yml`) is the API gateway/reverse proxy for all deployed student services
  as well as the `web` UI itself.
- Sablier (the "Sublier" serverless plugin referenced in the README) scales idle student services to zero
  and relies on Traefik middleware labels set by `traefik_repo`/`docker_repo` at deploy time.
