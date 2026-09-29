# URL Shortener

A simple web app that shortens long links and counts clicks.
Main goal: practice automated deployment with Docker, Kubernetes, Helm, and AWS.

## Architecture

```
                    ┌──────────────────────────────┐
Browser ──:8080──>  │ frontend (nginx)             │
                    │  /        -> static React app│
                    │  /api, /r -> backend:8000     │──> backend (FastAPI) ──> PostgreSQL
                    └──────────────────────────────┘
```

Only the frontend is exposed. The backend is reachable only from inside the Docker network
(in Kubernetes: a ClusterIP Service).

## Project structure

| Path | Contents |
|---|---|
| `backend/` | FastAPI application (Python, uv) and its `Dockerfile` |
| `frontend/` | React + Vite UI, nginx config template, and its `Dockerfile` |
| `compose.yaml` | Full local stack: db, migration, backend, frontend |

## Running with Docker Compose

Requires Docker only.

```bash
docker compose up --build
```

Open http://localhost:8080.

Startup order is enforced with `depends_on` conditions:

| Service | Image | Role | Starts after |
|---|---|---|---|
| `db` | `postgres:17-alpine` | Database (data in the `pgdata` volume) | — |
| `migration` | backend image | Runs `alembic upgrade head`, then exits | `db` is healthy |
| `backend` | backend image | API on port 8000 (internal only) | `migration` completed successfully |
| `frontend` | frontend image | nginx on port 8080 | `backend` is healthy (`/readyz`) |

```bash
docker compose down        # stop; data is kept in the pgdata volume
docker compose down -v     # stop and delete all data
```

## Container images

| Image | Base | Runs as | Notes |
|---|---|---|---|
| backend | `python:3.12-slim` (multi-stage, uv in builder only) | `appuser` | Same image runs the API and migrations |
| frontend | `nginxinc/nginx-unprivileged:1.29-alpine` (multi-stage, Node in builder only) | `nginx` | Listens on 8080 |

Runtime configuration (environment variables):

| Variable | Image | Example |
|---|---|---|
| `DATABASE_URL` | backend | `postgresql+psycopg://app:app@db:5432/urlshortener` |
| `BACKEND_URL` | frontend | `http://backend:8000` (rendered into the nginx config at startup) |

Health endpoints:

| Path | Container | Checks |
|---|---|---|
| `/healthz` | backend | Process is alive (liveness) |
| `/readyz` | backend | Database is reachable (readiness) |
| `/healthz` | frontend | nginx is serving (liveness/readiness) |

## Local development (without Docker for the app)

Requires Docker (for PostgreSQL), uv, and Node.js 24.

```bash
docker compose up -d db          # start PostgreSQL only
cd backend
cp .env.example .env             # local settings
uv run alembic upgrade head      # create/update DB tables
uv run uvicorn app.main:app --reload
```

- API docs: http://localhost:8000/docs

Frontend, in a second terminal:

```bash
cd frontend
npm ci
npm run dev
```

Open http://localhost:5173. The Vite dev server forwards `/api` and `/r` to the backend on port 8000
(override with `BACKEND_URL`).

## API

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/links` | Create a short link. Body: `{"target_url": "https://..."}` |
| `GET` | `/api/links?limit=50` | List links, newest first (max 100) |
| `GET` | `/r/{code}` | Redirect to the target URL (307) and count the click |

## Tests and lint

Tests run against a separate `urlshortener_test` database (created automatically).
Override it with `TEST_DATABASE_URL`.

```bash
cd backend
uv run pytest
uv run ruff check . && uv run ruff format --check .
```

## Roadmap

- [x] 1. Backend: FastAPI skeleton + `/healthz`
- [x] 2. Backend: PostgreSQL connection + migrations
- [x] 3. Backend: link shortening and redirect API
- [x] 4. Frontend: React UI
- [x] 5. Local setup: Dockerfiles + docker-compose
- [ ] 6. Push to GitHub + CI (tests, lint, image build)
- [ ] 7. Kubernetes manifests → Helm chart
- [ ] 8. AWS: ECR, EKS, RDS
- [ ] 9. CD: automated deployment
- [ ] 10. Observability: `/metrics` (Prometheus) + Grafana
