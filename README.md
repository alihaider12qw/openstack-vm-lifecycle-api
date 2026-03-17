# OpenStack VM Lifecycle API

REST API for managing OpenStack VM lifecycle operations, built as a production-oriented proof of concept.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Running Tests](#running-tests)
- [Quality Checks](#quality-checks)
- [Architecture](#architecture)
- [Design Choices](#design-choices)
- [SDLC & Engineering Artifacts](#sdlc--engineering-artifacts)
- [Engineering Skills Demonstrated](#engineering-skills-demonstrated)
- [Future Improvements](#future-improvements)

---

## Features

- `POST /v1/vms` — create a VM (201 + response body)
- `GET /v1/vms` — list VMs with pagination (`?limit=&offset=`)
- `GET /v1/vms/{vm_id}` — get VM details (UUID-validated)
- `POST /v1/vms/{vm_id}/start` — start a stopped VM
- `POST /v1/vms/{vm_id}/stop` — stop an active VM
- `POST /v1/vms/{vm_id}/reboot` — reboot an active VM
- `DELETE /v1/vms/{vm_id}` — delete a VM
- `GET /health` — health check

## Tech Stack

- Python 3.11+, FastAPI, Pydantic v2, pydantic-settings
- pytest (24 tests), ruff (lint), mypy (type-check)
- Docker / docker-compose
- GitHub Actions CI (lint → type-check → test → docker build)

## Project Structure

```text
app/
  api/
    deps.py                    # Dependency injection
    routes/vms.py              # REST endpoint handlers
  core/
    config.py                  # Environment-driven settings
    exceptions.py              # Exception hierarchy with error codes
    logging_config.py          # Structured logging setup
    middleware.py              # Request ID correlation middleware
    time.py                    # Shared UTC helper
  schemas/vm.py                # Pydantic request/response contracts
  services/
    openstack_client.py        # Adapter protocol + mock implementation
    vm_service.py              # Business logic with state machine guards
  main.py                      # App wiring, lifespan, error handlers, CORS
tests/
  conftest.py                  # Per-test fixtures for isolation
  test_vm_api.py               # 24 tests across 7 categories
docs/
  architecture.md
  sdlc.md
  roadmap-backlog.md
  agile-collaboration.md
Dockerfile
docker-compose.yml
requirements.txt               # Pinned production deps
requirements-dev.txt            # Dev/CI tooling
```

## Quick Start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

### Docker

```bash
docker compose up --build
```

## Running Tests

```bash
pip install -r requirements-dev.txt
pytest -v
```

## Quality Checks

```bash
ruff check .             # lint
ruff format --check .    # format check
mypy app/                # type check
```

## Architecture

Layered design with strict separation:

1. **API layer** — HTTP contracts, status codes, UUID path validation.
2. **Service layer** — lifecycle orchestration, state machine guards, logging.
3. **Adapter layer** — `OpenStackAdapter` protocol; `MockOpenStackClient` for local dev, drop-in real adapter slot.
4. **Schema layer** — Pydantic models for strict input/output validation.

See `docs/architecture.md` for full writeup.

## Design Choices

- **FastAPI** for typed contracts and auto-generated OpenAPI docs.
- **Adapter pattern** to decouple cloud provider from business logic.
- **State machine guards** prevent invalid transitions (e.g. starting an already-active VM returns 409).
- **Structured error responses** with machine-readable codes (`VM_NOT_FOUND`, `INVALID_STATE_TRANSITION`).
- **Request correlation IDs** via `X-Request-ID` header for distributed tracing.
- **Pagination** on list endpoint to bound memory and response size.
- **Per-test isolation** via fixtures to prevent cross-test state leakage.
- **Config-driven adapter selection** via `USE_MOCK_OPENSTACK` environment variable.

## SDLC & Engineering Artifacts

| Artifact                      | Location                      |
| ----------------------------- | ----------------------------- |
| Architecture & design writeup | `docs/architecture.md`        |
| SDLC process                  | `docs/sdlc.md`                |
| Agile collaboration evidence  | `docs/agile-collaboration.md` |
| Roadmap & backlog             | `docs/roadmap-backlog.md`     |
| Contribution workflow         | `CONTRIBUTING.md`             |
| CI pipeline                   | `.github/workflows/ci.yml`    |
| Dockerfile                    | `Dockerfile`                  |

## Engineering Skills Demonstrated

- **System design:** layered architecture, adapter protocol, state machine, structured errors.
- **Software development:** typed contracts, input validation, pagination, correlation IDs.
- **Testing:** 24 tests covering happy path, validation errors, state violations, 404s, and middleware.
- **DevOps:** Dockerfile, docker-compose, pinned deps, multi-stage CI (lint/type-check/test/docker).
- **Agile collaboration:** documented DoR/DoD, PR checklist, backlog-driven delivery, iterative roadmap.

## Future Improvements

See `docs/roadmap-backlog.md` for the full prioritized backlog.
