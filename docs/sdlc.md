# SDLC Approach

## 1) Requirements and Scope

### Functional requirements
- REST APIs for full VM lifecycle (create, list, get, start, stop, reboot, delete).
- Input validation with structured error responses.
- State machine enforcement for lifecycle transitions.
- Pagination on list endpoint.
- Health check endpoint.

### Non-functional requirements
- Clean layered architecture with adapter abstraction.
- Local testability without OpenStack dependency.
- Structured logging with request correlation IDs.
- Comprehensive documentation for design and future direction.
- Containerized deployment support.

## 2) Design

- Framework: **FastAPI** for typed API contracts, auto-generated OpenAPI docs, and async support.
- Architecture: **Layered with adapter abstraction** for testability and provider decoupling.
- Error strategy: exception hierarchy with machine-readable codes and global handlers.
- Config: environment-driven settings with `.env` support via `pydantic-settings`.

## 3) Implementation

- Schema-first Pydantic v2 models with field-level validation.
- Service orchestration with explicit state machine guards.
- Mock OpenStack adapter for reliable local behavior.
- Request ID correlation middleware for tracing.
- CORS middleware for cross-origin support.
- Proper dependency injection via `app.state` (no circular imports).

## 4) Verification

- 24 tests across 7 categories:
  - Health endpoint
  - VM creation (happy path + validation failures)
  - VM listing (empty, populated, pagination)
  - VM get (success, not found, invalid UUID)
  - Lifecycle actions (start, stop, reboot, delete)
  - State transition guards (invalid transitions → 409)
  - Correlation ID middleware behavior
- Per-test isolation via pytest fixtures.
- Linting: `ruff check` + `ruff format --check`.
- Type checking: `mypy --strict` mode.

## 5) Release / Operate

- Run locally with Uvicorn or via `docker compose up`.
- OpenAPI docs at `/docs` and `/redoc`.
- CI pipeline: lint → type-check → test → docker build.
- Productionization roadmap in `docs/roadmap-backlog.md`.

## 6) Agile Collaboration

- Work executed in a short time-box with iterative increments.
- Backlog-driven prioritization captured in `docs/roadmap-backlog.md`.
- Contribution and review workflow documented in `CONTRIBUTING.md`.
- Definition of Ready/Done used to keep scope and quality explicit.
- CI checks provide automated feedback on every push/PR.

## 7) Evidence Map

| Artifact | Location |
|---|---|
| Architecture decisions | `docs/architecture.md` |
| SDLC process | `docs/sdlc.md` |
| Agile collaboration | `docs/agile-collaboration.md` |
| Backlog and roadmap | `docs/roadmap-backlog.md` |
| Tests (24) | `tests/test_vm_api.py` |
| CI pipeline | `.github/workflows/ci.yml` |
| Container support | `Dockerfile`, `docker-compose.yml` |
