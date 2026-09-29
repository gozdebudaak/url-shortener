# URL Shortener

A simple web app that shortens long links and counts clicks.
Main goal: practice automated deployment with Docker, Kubernetes, Helm, and AWS.

## Architecture

```
Browser ──> frontend (React + nginx) ──> backend (FastAPI) ──> PostgreSQL
```

## Project structure

| Directory | Contents |
|---|---|
| `backend/` | FastAPI application (Python, uv) |
| `frontend/` | React + Vite UI |
| `compose.yaml` | Local PostgreSQL |

## Running locally

Requires Docker, uv, and Node.js 24.

```bash
docker compose up -d db          # start PostgreSQL
cd backend
cp .env.example .env             # local settings
uv run alembic upgrade head      # create/update DB tables
uv run uvicorn app.main:app --reload
```

- Liveness: http://localhost:8000/healthz
- Readiness (checks DB): http://localhost:8000/readyz
- API docs: http://localhost:8000/docs

Frontend (requires Node.js 24, in a second terminal):

```bash
cd frontend
npm ci
npm run dev
```

Open http://localhost:5173. The Vite dev server forwards `/api` and `/r` to the backend on port 8000.

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
- [ ] 5. Local setup: Dockerfiles + docker-compose
- [ ] 6. Push to GitHub + CI (tests, lint, image build)
- [ ] 7. Kubernetes manifests → Helm chart
- [ ] 8. AWS: ECR, EKS, RDS
- [ ] 9. CD: automated deployment
- [ ] 10. Observability: `/metrics` (Prometheus) + Grafana
