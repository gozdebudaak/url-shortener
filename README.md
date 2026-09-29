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

## Running locally

Requires Docker and uv.

```bash
docker compose up -d db          # start PostgreSQL
cd backend
cp .env.example .env             # local settings
uv run uvicorn app.main:app --reload
```

- Liveness: http://localhost:8000/healthz
- Readiness (checks DB): http://localhost:8000/readyz
- API docs: http://localhost:8000/docs

## Roadmap

- [x] 1. Backend: FastAPI skeleton + `/healthz`
- [ ] 2. Backend: PostgreSQL connection + migrations
- [ ] 3. Backend: link shortening and redirect API
- [ ] 4. Backend: `/metrics` (Prometheus)
- [ ] 5. Frontend: React UI
- [ ] 6. Local setup: Dockerfiles + docker-compose
- [ ] 7. Push to GitHub + CI (tests, lint, image build)
- [ ] 8. Kubernetes manifests → Helm chart
- [ ] 9. AWS: ECR, EKS, RDS
- [ ] 10. CD: automated deployment
