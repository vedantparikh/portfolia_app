#!/usr/bin/env bash
# Alembic on a throwaway Postgres: upgrade from empty, no model drift, full downgrade, upgrade again.
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT=$PWD
PROJECT=${COMPOSE_PROJECT_NAME:-portfolio}
NAME="$PROJECT-migcheck-$$"

cleanup() {
  docker rm -f "$NAME-db" >/dev/null 2>&1 || true
  docker network rm "$NAME" >/dev/null 2>&1 || true
}
trap cleanup EXIT

docker network create "$NAME" >/dev/null
docker run -d --name "$NAME-db" --network "$NAME" \
  -e POSTGRES_USER=migcheck -e POSTGRES_PASSWORD=migcheck -e POSTGRES_DB=migcheck \
  "$PROJECT-postgres" >/dev/null
for _ in $(seq 60); do
  docker exec "$NAME-db" pg_isready -U migcheck -d migcheck -h 127.0.0.1 >/dev/null 2>&1 && break
  sleep 1
done

docker run --rm --network "$NAME" --user "$(id -u):$(id -g)" \
  -v "$ROOT/python/app:/app" -w /app -e HOME=/tmp -e PYTHONDONTWRITEBYTECODE=1 \
  -e POSTGRES_HOST="$NAME-db" -e POSTGRES_PORT=5432 \
  -e POSTGRES_USER=migcheck -e POSTGRES_PASSWORD=migcheck -e POSTGRES_DB=migcheck \
  "$PROJECT-api" sh -ec '
    alembic upgrade head
    alembic check
    alembic downgrade base
    python - <<EOF
from sqlalchemy import create_engine, text
from config import settings
with create_engine(settings.DATABASE_URL).connect() as c:
    left = c.execute(text(
        "select relname from pg_class join pg_namespace n on n.oid = relnamespace "
        "where nspname = current_schema() and relkind in (\x27r\x27, \x27S\x27) and relname <> \x27alembic_version\x27 "
        "union all select typname from pg_type join pg_namespace n on n.oid = typnamespace "
        "where nspname = current_schema() and typtype = \x27e\x27"
    )).scalars().all()
assert not left, f"downgrade left objects behind: {left}"
EOF
    alembic upgrade head
    alembic check' 2>&1 | { grep -v '^INFO ' || true; }
