#!/usr/bin/env bash
# Pre-push gate mirroring CI. Needs only Docker (the Jetson host has no py3.12/node).
#   scripts/verify.sh          compose config + lint + backend tests + frontend build
#   scripts/verify.sh --stack  also rebuild/restart the local stack and smoke-test it
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT=$PWD
PROJECT=${COMPOSE_PROJECT_NAME:-portfolio}

step() { printf '\n== %s\n' "$*"; }

step "compose config"
docker compose config -q

step "build images"
docker compose build -q api app

step "lint: ruff (backend), eslint (frontend)"
docker run --rm --user "$(id -u):$(id -g)" -v "$ROOT/python/app:/app" -w /app \
  "$PROJECT-api" sh -c 'ruff check --no-cache . && ruff format --check --no-cache .'
docker run --rm --network none \
  -v "$ROOT/js/src:/app/src:ro" -v "$ROOT/js/.eslintrc.cjs:/app/.eslintrc.cjs:ro" \
  -v "$ROOT/js/vite.config.js:/app/vite.config.js:ro" \
  "$PROJECT-app" npx eslint . --ext js,jsx --report-unused-disable-directives --max-warnings 0

step "backend: app import + pytest (throwaway container, not on the stack network)"
docker run --rm --user "$(id -u):$(id -g)" \
  -v "$ROOT/python/app:/app" -w /app \
  -e HOME=/tmp -e TESTING=true -e TEST_DATABASE_URL=sqlite:////tmp/test.db \
  -e PYTHONPATH=/app:/tmp/extra -e PYTHONDONTWRITEBYTECODE=1 \
  "$PROJECT-api" sh -c '
    pip install -q --disable-pip-version-check --no-deps --target /tmp/extra ta &&
    python -c "import main; assert len(main.app.routes) > 100" &&
    python -m pytest tests -q -p no:cacheprovider'

step "frontend: production build"
docker run --rm --network none \
  -v "$ROOT/js/src:/app/src:ro" -v "$ROOT/js/vite.config.js:/app/vite.config.js:ro" \
  "$PROJECT-app" npx vite build --outDir /tmp/dist --logLevel warn

if [[ "${1:-}" == "--stack" ]]; then
  step "stack: up + smoke"
  docker compose up -d --wait --wait-timeout 300
  for url in "http://localhost:${PORTFOLIO_UI_PORT:-3000}/" \
             "http://localhost:${PORTFOLIO_UI_PORT:-3000}/api/v1/health" \
             "http://127.0.0.1:${PORTFOLIO_API_PORT:-8000}/health/"; do
    for attempt in 1 2 3 4 5 6; do
      curl -fsS -o /dev/null --max-time 10 "$url" && break
      [[ $attempt == 6 ]] && { echo "FAIL $url"; exit 1; }
      sleep 5
    done
    echo "ok  $url"
  done
fi

step "all checks passed"
