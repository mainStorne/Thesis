#!/bin/bash
set -eu

cd "$(dirname "$0")"

log()  { echo "==> $*"; }
fail() { echo "FAILED: $*" >&2; exit 1; }

# 1. Config bootstrap — auto-create gitignored local config from the
#    checked-in examples if missing, instead of failing on a missing file.
if [ ! -f ../.env ]; then
    log "../.env missing, creating from ../.env.example"
    cp ../.env.example ../.env || fail "could not create ../.env"
fi

if [ ! -f settings.yml ]; then
    log "settings.yml missing, creating from settings.example.yml"
    cp settings.example.yml settings.yml || fail "could not create settings.yml"
fi

# 2. Docker Swarm must be active for create-registry.sh's `docker service create`.
if [ "$(docker info --format '{{.Swarm.LocalNodeState}}' 2>/dev/null || true)" != "active" ]; then
    log "Docker Swarm not active, initializing"
    docker swarm init || fail "docker swarm init"
fi

# 3. Local registry — idempotent: skip if it already exists instead of
#    re-running create-registry.sh and hitting "service already exists".
if docker service ls --filter name=registry -q | grep -q .; then
    log "Registry already exists, skipping create-registry.sh"
else
    log "Creating local registry"
    sh ../create-registry.sh || fail "create-registry.sh"
fi

# 4. Postgres
log "Starting postgres"
docker compose up -d || fail "docker compose up -d"

log "Waiting for postgres to accept connections"
for i in $(seq 1 30); do
    if docker compose exec -T db pg_isready >/dev/null 2>&1; then
        break
    fi
    if [ "$i" -eq 30 ]; then
        fail "postgres did not become ready within 30s"
    fi
    sleep 1
done

# 5. Python deps
log "Installing python dependencies"
uv sync || fail "uv sync"

# 6. Migrations — `uv run` so alembic resolves from .venv, not $PATH
log "Running migrations"
uv run sh alembic.sh || fail "alembic.sh"

# 7. Run — `uv run` for the same reason, `--reload` since this is a dev loop
log "Starting web service"
uv run uvicorn main:app --reload