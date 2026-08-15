# Personalized Healthcare Recommendation System — Architecture

## Overview
This document describes the full-stack architecture, components, and integration patterns for the Personalized Healthcare Recommendation System.

High-level components:
- Frontend: React + Vite + Tailwind CSS (SPA) — UI, visualization, auth flows.
- Backend API: FastAPI + SQLAlchemy + PostgreSQL — REST API, RBAC, orchestration, metrics.
- ML Service: Dedicated Python service for model inference & feature pipelines. Models are versioned and registered via MLflow.
- Background Workers: Celery + Redis for long-running tasks (training, retraining, batch inference).
- Storage: PostgreSQL for transactional data; object store (S3) or local `ml/models/` for artifacts.
- Observability: Prometheus for metrics, Grafana for dashboards, centralized logging (ELK/Datadog).

## Communication patterns
- Frontend <-> Backend: REST JSON over HTTPS. Auth via Bearer tokens (JWT). UI receives predictions and recommendations via `/api/*` endpoints.
- Backend <-> ML Service: gRPC/HTTP REST for inference. The backend should call a low-latency inference endpoint; a local in-process client may be used in small deployments.
- Backend <-> Workers: Task queue (Redis) enqueues training/retraining jobs for workers.
- Backend/Workers <-> MLflow: Log runs, metrics, and artifacts to MLflow; store model version metadata in DB.

## Security model
- JWT access + refresh tokens; refresh token rotation recommended.
- RBAC roles: `USER`, `ANALYST`, `ADMIN` with `require_role` and `require_any_role` dependency functions.
- Input validation via Pydantic; size limits and rate limiting via middleware; CORS restricted using `ALLOWED_ORIGINS` env var.

## Deployment
- Containerize services (backend, ml-service, worker). Use Kubernetes or docker-compose for local dev.
- Use managed Postgres in production; secrets in a secrets manager.

## Filemap (scaffold)
- `frontend/` — React app (Vite)
- `backend/` — FastAPI app skeleton
- `ml/` — model training, inference, and data pipelines
- `docs/` — architecture and API specs
- `tests/` — unit/integration tests
- `docker-compose.yml` — local dev compose file

## Next steps
- Fill in each service implementation, especially the ML inference API and background worker flows.
- Add deployment manifests (Helm/Kustomize) for production clusters.
