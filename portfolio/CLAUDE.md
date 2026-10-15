# Portfolia

Self-hosted investment-portfolio tracker (holdings, P&L, TWR/XIRR, risk metrics, watchlists, broker-PDF import). FastAPI + SQLAlchemy 2 (sync) + Postgres 16 + Redis + yfinance backend (`python/app`); React 18 + Vite + Tailwind frontend (`js`).

Git root is the parent dir (`../`: `.github/workflows/ci.yml`, `.pre-commit-config.yaml`). Roadmap, release strategy and progress log: `REFACTOR_PLAN.md`.

## Host: shared NVIDIA Jetson AGX Xavier (prod server)
- arm64, JetPack 5.1.6/CUDA 11.4, 30 GB unified RAM, ~35 other containers (immich, jellyfin, ollama use the GPU). The Docker data-root is `/mnt/samsung_ufs/docker_data`, and eMMC `/` is nearly full.
- Host `python3` is 3.8 and there is no host `node`. **Everything runs through Docker.**
- Never touch other projects' containers, networks or volumes. Portfolio only publishes UI :3000 and API on 127.0.0.1:8000. DB/Redis stay unpublished.
- No GPU in portfolio images by default. GPU work goes through shared `ollama` or an opt-in `gpu` profile with a CPU fallback (plan §1b).

## Quick commands (cwd `portfolio/`)
```
scripts/verify.sh            # the gate: compose config, pytest in API image, vite prod build (~2 min)
scripts/verify.sh --stack    # + rebuild/restart local stack and smoke-test UI, /api proxy, API health
docker compose up -d --wait  # run stack → UI http://localhost:3000, API http://127.0.0.1:8000/docs
docker compose logs -f api
```
Single test file (same env as the gate):
```
docker run --rm --user "$(id -u):$(id -g)" -e HOME=/tmp -v "$PWD/python/app:/app" -w /app -e TESTING=true -e TEST_DATABASE_URL=sqlite:////tmp/t.db \
  -e PYTHONDONTWRITEBYTECODE=1 portfolio-api python -m pytest tests/unit/test_position_and_returns.py -q -p no:cacheprovider
```
Lint is part of the gate, and both linters must report 0. Autofix before committing:
```
docker run --rm --user "$(id -u):$(id -g)" -v "$PWD/python/app:/app" -w /app portfolio-api sh -c 'ruff check --fix --no-cache . && ruff format --no-cache .'
docker run --rm -v "$PWD/js/src:/app/src" -v "$PWD/js/eslint.config.js:/app/eslint.config.js:ro" portfolio-app npx eslint src --fix
```
Never run pytest inside the running `portfolio-api-1`, which is wired to the stack's Postgres.

## Architecture & patterns
- **Imports are rooted at `python/app`**: `from core.services...`, `from api.v1...`. Never `app.core...`.
- **Backend layers:** `api/v1/<feature>/router.py` → `core/services/<x>_service.py` (class takes `db: Session` in `__init__`) → `core/database/models/*` (legacy `Column` style, `Numeric` money). Pydantic schemas live in `core/schemas/<feature>.py`. There is no repository layer yet. New code puts queries and commits in services, not routers.
- **Router mounting** is in `main.py` (try/import blocks), with prefix `/api/v1/<feature>`. Watch route order: literal paths go before `/{id}`.
- **Auth:** `Depends(get_current_active_user)` from `core/auth/dependencies.py`. Every resource must be scoped by `user_id`.
- **Errors:** services raise domain errors (`OversellError` in `portfolio_service.py`, `ValueError`). Routers map them to `HTTPException`. Don't put `str(e)` in a response `detail`.
- **Financial math:** the canonical position engine is `compute_position` (FIFO lots, fees) in `core/services/portfolio_service.py`. Returns, TWR and XIRR are in `portfolio_calculation_service.py`. Reuse these; never add another copy of a metric. Percent units are 15.0, not 0.15. The frontend displays backend values and never computes them.
- **Market data** goes only through `core/services/market_data_service.py` (Redis-cached yfinance). Tests mock it and never hit the network.
- **Schema:** models plus Alembic. The only migration is currently a no-op and the app still calls `create_all`. Schema changes need a real migration, and must be expand/contract: additive in release N, destructive in N+1.
- **Frontend:** pages and components are in `js/src/components/<feature>/` (with an `index.js` barrel). All HTTP calls go through the axios objects in `js/src/services/api.js`. Auth state is in `contexts/AuthContext.jsx`. Data fetching is `useEffect`+`useState`, errors are shown with `react-hot-toast`, and formatting goes through `utils/formatters.jsx` (no inline `toFixed` or `$`).
- **Config:** `config.py` `settings`, fed by compose `env_file` (`python/app/.env.docker`, `js/.env.docker`). These are gitignored secrets: never print or commit them. When you add a key, also add it to the matching `.env.example`.
- **Compose:** `docker-compose.yml` is currently the dev stack (bind mounts, reload, Vite dev server) with memory limits and log rotation. It must keep working from the `.env.example` templates, because CI runs it that way.

## Rules of engagement
- Never add, upgrade or remove a dependency (pip, npm, base image, GitHub Action) without asking first.
- After touching code, run the matching test file. **Before every commit, `scripts/verify.sh` must pass**, plus `--stack` if Docker, compose, env or startup changed. Never commit a red gate. CI runs the same script on arm64 and is a required check.
- One logical change per commit, using Conventional Commits (`feat:`, `fix:`, `chore:`, `ci:`, `docs:`). Work on a branch, never directly on `master`. Don't push or open PRs unless asked.
- `python/app/tests/quarantine.txt` only shrinks. Never add entries to hide a new failure. When a fix makes a quarantined test pass, delete its line (strict xfail fails otherwise).
- Don't write unnecessary comments, docstrings, tutorial-style text or boilerplate. Match the surrounding style.
- Ask before deleting Docker volumes, changing published ports or touching anything outside `portfolio/`.
- When a session establishes a new non-obvious fact about the project, update this file or the plan's progress log.

## Known state (2026-10-15)
- Gate: lint clean (ruff + eslint, 0 warnings); about 130 tests passed, 42 quarantined xfail, plus 8 quarantined uncollectable files.
- Lint policy: ruff ignores E501 (the formatter owns line length) and E712 (SQLAlchemy `== True`). ESLint has `react/prop-types` off (TS migration is planned). Use `eslint-disable-next-line react-hooks/exhaustive-deps -- <reason>` only when adding the dependency would change when the effect runs.
- `npm test` is a placeholder. There are no frontend unit tests or e2e tests yet.
