# Roadmap and Backlog

## Table of Contents

- [Time-Box Outcome (Completed)](#time-box-outcome-completed)
- [Near-Term Roadmap (1-2 sprints)](#near-term-roadmap-1-2-sprints)
  - [1. Real OpenStack Adapter](#1-real-openstack-adapter)
  - [2. Database Persistence](#2-database-persistence)
  - [3. Authentication & Authorization](#3-authentication--authorization)
  - [4. CI/CD Hardening](#4-cicd-hardening)
  - [5. JSON Structured Logging](#5-json-structured-logging)
- [Mid-Term Roadmap (3-5 sprints)](#mid-term-roadmap-3-5-sprints)
  - [6. Async Operation Handling](#6-async-operation-handling)
  - [7. Observability Stack](#7-observability-stack)
  - [8. API Maturity](#8-api-maturity)
  - [9. Multi-Tenancy & Access Control](#9-multi-tenancy--access-control)
  - [10. Secret & Configuration Management](#10-secret--configuration-management)
- [Long-Term Backlog (Prioritized)](#long-term-backlog-prioritized)
  - [P0 — Must-have for production](#p0--must-have-for-production)
  - [P1 — Operational excellence](#p1--operational-excellence)
  - [P2 — Advanced capabilities](#p2--advanced-capabilities)

---

## Time-Box Outcome (Completed)

- REST endpoints for full VM lifecycle (create, list, get, start, stop, reboot, delete).
- Layered architecture with adapter protocol abstraction.
- Mock OpenStack implementation for local POC execution.
- State machine guards preventing invalid lifecycle transitions (409).
- Structured error responses with machine-readable error codes.
- UUID-validated path parameters rejecting malformed IDs (422).
- Pagination on list endpoint with total count.
- Request correlation ID middleware (`X-Request-ID`).
- Structured logging across service layer.
- CORS middleware support.
- Proper dependency injection (no circular imports).
- 24 automated tests across 7 categories with per-test isolation.
- CI pipeline: lint (ruff) → type-check (mypy) → test (pytest) → docker build.
- Dockerfile and docker-compose for containerized deployment.
- Pinned dependency versions for reproducible builds.
- Project documentation (README, architecture, SDLC, agile collaboration).

---

## Near-Term Roadmap (1-2 sprints)

### 1. Real OpenStack Adapter
- Implement `RealOpenStackClient` using `openstacksdk` with Keystone authentication.
- Map OpenStack Nova exceptions to the app's error hierarchy (e.g. `openstack.exceptions.HttpException` → `OpenStackConnectionError`).
- Add retry with exponential backoff for transient 503/429 responses from Nova.
- Wire adapter selection in `main.py` lifespan based on `USE_MOCK_OPENSTACK` flag.

### 2. Database Persistence
- Replace in-memory dict with PostgreSQL via SQLAlchemy async.
- Add Alembic migration framework for schema versioning.
- Store VM records, status history, and operation audit trail.
- Add `DATABASE_URL` to config with connection pooling (`asyncpg`).

### 3. Authentication & Authorization
- Add JWT bearer token validation middleware.
- Integrate with an external identity provider (Keystone / Auth0 / Okta).
- Implement RBAC: `admin` (all operations), `operator` (start/stop/reboot), `viewer` (read-only).
- Scope VM visibility to the authenticated tenant/project.

### 4. CI/CD Hardening
- Add `pip-audit` for dependency vulnerability scanning.
- Add `bandit` for static security analysis.
- Add `pytest-cov` with minimum coverage gate (e.g. 85%).
- Add CD stage: build + push Docker image to container registry on tag.
- Add environment promotion pipeline: dev → staging → production.

### 5. JSON Structured Logging
- Switch log formatter to JSON output (e.g. `python-json-logger`).
- Include `request_id`, `user_id`, `vm_id`, `action`, `duration_ms` in every log line.
- Configure log level per environment (DEBUG in dev, WARNING in prod).
- Integrate with centralized log aggregator (ELK / CloudWatch / Datadog).

---

## Mid-Term Roadmap (3-5 sprints)

### 6. Async Operation Handling
- Long-running operations (create, delete) return `202 Accepted` with an operation ID.
- Add task queue (Celery + Redis, or ARQ) to process operations asynchronously.
- Add `GET /v1/operations/{op_id}` endpoint for clients to poll status.
- Add optional webhook callback URL on action requests for push-based notification.

### 7. Observability Stack
- Expose `/metrics` endpoint with Prometheus client (request count, latency histograms, error rates, active VMs by status).
- Add OpenTelemetry tracing across API → service → adapter layers.
- Enhance `/health` to deep-check database connectivity and OpenStack API reachability; report `healthy` / `degraded` / `unhealthy`.
- Add structured alerting rules for error rate spikes and latency degradation.

### 8. API Maturity
- Add filtering on list: `?status=ACTIVE`, `?name=prefix*`.
- Add sorting: `?sort=created_at:desc`.
- Add cursor-based pagination for large datasets (replace offset).
- Add idempotency keys on mutating endpoints to prevent duplicate operations.
- Add `ETag` / `If-Match` headers for optimistic concurrency on updates.
- Add API rate limiting per client/tenant (token bucket via Redis).

### 9. Multi-Tenancy & Access Control
- Add `project_id` / `tenant_id` scoping on all VM records.
- Enforce tenant isolation at the database query level.
- Add quota management per tenant (max VMs, max vCPUs).
- Add admin API for tenant and quota management.

### 10. Secret & Configuration Management
- Migrate credentials to a secret manager (HashiCorp Vault / AWS Secrets Manager).
- Add dynamic config reload without restart (feature flags, quota limits).
- Separate runtime config from deployment config.

---

## Long-Term Backlog (Prioritized)

### P0 — Must-have for production
- TLS termination guidance and security headers (`Strict-Transport-Security`, `X-Content-Type-Options`).
- Request body size limits to prevent abuse.
- Graceful shutdown: drain in-flight requests before process exit.
- Database connection pool tuning and read-replica routing.
- Disaster recovery: automated database backups with point-in-time restore.

### P1 — Operational excellence
- Kubernetes deployment manifests (Deployment, Service, Ingress, HPA).
- Helm chart with environment-specific value overrides.
- Horizontal pod autoscaling based on request latency / queue depth.
- Blue-green or canary deployment strategy.
- Runbook documentation for common operational scenarios (failover, rollback, scaling).

### P2 — Advanced capabilities
- VM snapshot and restore API endpoints.
- Bulk operations API (batch create/delete).
- Dashboard service for lifecycle analytics and fleet visibility.
- Chaos engineering test suite (network partitions, adapter timeouts, DB failures).
- SDK / client library generation from OpenAPI spec.
- Event-driven architecture: publish VM lifecycle events to a message bus (Kafka / SNS) for downstream consumers.
