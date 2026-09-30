# URL Shortener

[![CI](https://github.com/gozdebudaak/url-shortener/actions/workflows/ci.yml/badge.svg)](https://github.com/gozdebudaak/url-shortener/actions/workflows/ci.yml)

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
| `.github/workflows/ci.yml` | CI pipeline (GitHub Actions) |
| `helm/url-shortener/` | Helm chart: backend, frontend, migration hook |
| `k8s/` | Namespace and a dev-only PostgreSQL for local clusters (not part of the chart) |

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

## Running on Kubernetes (local)

Tested with Docker Desktop Kubernetes (**kubeadm** mode, so locally built images are visible to the cluster).

### What the chart manages

| Resource | Name | Notes |
|---|---|---|
| Job (Helm hook) | `<release>-migration` | `pre-install,pre-upgrade`: runs `alembic upgrade head` before any app pod changes |
| Deployment + Service | `<release>-backend` | ClusterIP, port 8000. Liveness `/healthz`, readiness `/readyz` |
| Deployment + Service | `<release>-frontend` | ClusterIP, port 80 → container 8080 |

Not managed by the chart:

- **Database.** Locally: `k8s/dev/postgres.yaml`. On AWS: RDS.
- **Database Secret.** Created outside the chart so the password never lands in values files or git.
  The chart only references it by name (`backend.databaseSecret`).

### Install

```bash
# 1. Build images (the cluster uses them directly, no registry needed)
docker build -t url-shortener-backend:dev backend
docker build -t url-shortener-frontend:dev frontend

# 2. Namespace, dev database, and DB secret
kubectl apply -f k8s/namespace.yaml -f k8s/dev/postgres.yaml
kubectl -n url-shortener create secret generic backend-db \
  --from-literal=DATABASE_URL='postgresql+psycopg://app:app@postgres:5432/urlshortener'

# 3. Install the chart (waits for the migration hook and all pods)
helm install url-shortener helm/url-shortener -n url-shortener --wait --timeout 3m

# 4. Open the app at http://localhost:8081
kubectl -n url-shortener port-forward svc/url-shortener-frontend 8081:80
```

### Upgrade and rollback

```bash
helm upgrade url-shortener helm/url-shortener -n url-shortener --set backend.replicas=3 --wait
helm -n url-shortener history url-shortener
helm -n url-shortener rollback url-shortener <revision>
```

If the migration hook fails, the upgrade is marked `failed` and the app Deployments are **not** changed:
the previous pods keep serving traffic. The failed Job is kept for debugging
(`kubectl -n url-shortener logs job/url-shortener-migration`) and replaced on the next upgrade.

Always pass image tags as strings (`--set-string backend.image.tag=<sha>`).
With plain `--set` or unquoted YAML, tags like `1.20` or `1234e5` are parsed as numbers.

### Chart values

| Key | Default | Description |
|---|---|---|
| `backend.image.repository` | `url-shortener-backend` | Backend image (also used by the migration Job) |
| `backend.image.tag` | `"dev"` | Backend image tag |
| `backend.image.pullPolicy` | `IfNotPresent` | |
| `backend.replicas` | `2` | |
| `backend.databaseSecret` | `backend-db` | Existing Secret with a `DATABASE_URL` key |
| `backend.resources` | 100m / 128Mi request, 256Mi limit | No CPU limit on purpose (avoids throttling) |
| `frontend.image.repository` | `url-shortener-frontend` | |
| `frontend.image.tag` | `"dev"` | |
| `frontend.image.pullPolicy` | `IfNotPresent` | |
| `frontend.replicas` | `2` | |
| `frontend.resources` | 50m / 64Mi request, 128Mi limit | |

`BACKEND_URL` for the frontend is set by the chart (`http://<release>-backend:8000`), not by values.

### Security defaults

All containers (backend, frontend, migration) run with `runAsNonRoot: true` and `allowPrivilegeEscalation: false`.
Images use numeric users (backend `10001`, frontend `101`) so Kubernetes can verify they are not root.

### Clean up

```bash
helm -n url-shortener uninstall url-shortener
kubectl delete namespace url-shortener   # also deletes the dev database and its volume
```

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

## CI

Runs on every push to `main` and on pull requests to `main`
([`.github/workflows/ci.yml`](.github/workflows/ci.yml)).

```
 backend  ──┐
 (lint,     │
  tests)    ├──> images (backend)    ─ docker build
            │    images (frontend)   ─ docker build
 frontend ──┘
 (npm build)
```

| Job | Steps | Notes |
|---|---|---|
| `backend` | `uv sync --locked`, `ruff check`, `ruff format --check`, `pytest` | Tests run against a PostgreSQL service container |
| `frontend` | `npm ci`, `npm run build` | Node version comes from `frontend/.nvmrc` |
| `images` | Build both Docker images (matrix: `backend`, `frontend`) | Runs only if both jobs above pass. Not pushed yet. |

- `backend` and `frontend` run in parallel. The two `images` jobs also run in parallel.
- Images are tagged with the commit SHA (`url-shortener-<service>:<sha>`), never `latest`.
- Docker layers are cached in the GitHub Actions cache (one scope per image).
  With a warm cache, an image build takes seconds instead of ~30s.
- uv and npm downloads are cached too.

## Roadmap

- [x] 1. Backend: FastAPI skeleton + `/healthz`
- [x] 2. Backend: PostgreSQL connection + migrations
- [x] 3. Backend: link shortening and redirect API
- [x] 4. Frontend: React UI
- [x] 5. Local setup: Dockerfiles + docker-compose
- [x] 6. Push to GitHub + CI (tests, lint, image build)
- [x] 7. Kubernetes manifests → Helm chart
- [ ] 8. AWS: ECR, EKS, RDS
- [ ] 9. CD: automated deployment
- [ ] 10. Observability: `/metrics` (Prometheus) + Grafana
