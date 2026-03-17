# Architecture and Design

## Overview

REST API for OpenStack VM lifecycle management with a layered, provider-decoupled design.

## High-Level Components

```text
┌──────────────────────────────────────────────────┐
│  HTTP / Middleware                               │
│  (CORS, Request ID correlation, error handlers)  │
├──────────────────────────────────────────────────┤
│  API Layer  (app/api/)                           │
│  Routes, UUID path validation, pagination params │
├──────────────────────────────────────────────────┤
│  Service Layer  (app/services/vm_service.py)     │
│  Business logic, state machine guards, logging   │
├──────────────────────────────────────────────────┤
│  Adapter Layer  (app/services/openstack_client)  │
│  OpenStackAdapter protocol + implementations     │
├──────────────────────────────────────────────────┤
│  Schema Layer  (app/schemas/)                    │
│  Pydantic models for strict contracts            │
├──────────────────────────────────────────────────┤
│  Core Layer  (app/core/)                         │
│  Config, exceptions, middleware, logging, time   │
└──────────────────────────────────────────────────┘
```

### API Layer (`app/api/`)

- REST routes with versioned prefix (`/v1/vms`).
- UUID-validated path parameters reject malformed IDs at the HTTP boundary.
- Pagination via `limit`/`offset` query parameters on list endpoint.
- Dependency injection via `app/api/deps.py` using FastAPI's `Depends` and `app.state`.

### Service Layer (`app/services/vm_service.py`)

- Orchestrates lifecycle operations against the adapter.
- **State machine guards**: validates the VM is in a permitted state before dispatching an action (e.g. only stopped VMs can be started). Returns structured 409 on violation.
- Structured logging for every mutating operation.

### Adapter Layer (`app/services/openstack_client.py`)

- `OpenStackAdapter` — Python `Protocol` defining the contract.
- `MockOpenStackClient` — in-memory implementation for local dev and tests.
- Config-driven selection: `USE_MOCK_OPENSTACK=true|false` in `app/main.py` lifespan.

### Schema Layer (`app/schemas/`)

- Pydantic v2 models with field-level validation (lengths, regex patterns).
- `VMStatus` as `StrEnum` for type-safe status values.
- `ErrorResponse` / `ErrorDetail` for structured error payloads.

### Core Layer (`app/core/`)

- `config.py` — environment-driven settings via `pydantic-settings`.
- `exceptions.py` — exception hierarchy (`AppError` → `VMNotFoundError`, `InvalidStateTransitionError`, etc.) with machine-readable error codes.
- `middleware.py` — `X-Request-ID` correlation middleware with latency logging.
- `logging_config.py` — centralized structured logging setup.
- `time.py` — single `utcnow()` helper (no duplication).

## Error Handling Strategy

- `VMNotFoundError` → **404** with `{"error": {"code": "VM_NOT_FOUND", ...}}`
- `InvalidStateTransitionError` → **409** with `{"error": {"code": "INVALID_STATE_TRANSITION", ...}}`
- `AppError` (catch-all) → **500** with code
- Unhandled `Exception` → **500** with generic message (no stack trace leak)
- Pydantic validation → **422** (FastAPI default)

## API Design Notes

- Base path: `/v1/vms` with explicit versioning.
- Noun-based resource URIs; lifecycle actions as sub-resource verbs.
- Soft deletion: status becomes `DELETED`; excluded from list and treated as 404 on get.
- Pagination: `?limit=50&offset=0` with `total` count in response.

## State Machine

```text
  create
    │
    ▼
  ACTIVE ──stop──▶ SHUTOFF ──start──▶ ACTIVE
    │                 │
    ├──reboot──▶ REBOOT                │
    │                                  │
    ├──delete──▶ DELETED ◀──delete─────┘
    │
  ERROR ──delete──▶ DELETED
```

Invalid transitions return 409 with `INVALID_STATE_TRANSITION`.

## Future Production Enhancements

- Real OpenStack adapter using `openstacksdk`.
- Async background tasking for long-running operations.
- API auth (JWT/OAuth2) and RBAC enforcement.
- Database persistence (PostgreSQL + Alembic migrations).
- Observability: Prometheus metrics, OpenTelemetry tracing, deep health checks.
