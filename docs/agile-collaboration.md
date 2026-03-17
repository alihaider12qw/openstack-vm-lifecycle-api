# Agile Collaboration Evidence

This document captures the team-oriented delivery practices used for this proof-of-concept.

## Delivery Cadence

- Iteration model: short, time-boxed sprint.
- Daily sync: progress, blockers, next actions.
- End-of-sprint review: demo working API behavior.
- Retrospective: identify one improvement for the next sprint.

## Backlog-Driven Delivery

Work was sequenced from core value to hardening:

1. API skeleton and contracts
2. VM lifecycle business logic
3. Mock OpenStack adapter for local reliability
4. API tests and documentation
5. Productionization roadmap and risk follow-ups

Backlog and roadmap are tracked in `docs/roadmap-backlog.md`.

## Collaboration Artifacts Included

- Product/engineering README: `README.md`
- Architecture decision writeup: `docs/architecture.md`
- SDLC process notes: `docs/sdlc.md`
- Prioritized roadmap/backlog: `docs/roadmap-backlog.md`
- Contribution and PR workflow: `CONTRIBUTING.md`
- Automated quality gate: `.github/workflows/ci.yml`

## Quality and Transparency Practices

- Explicit acceptance criteria expressed as API behavior and tests.
- Pull request checklist to enforce test, docs, and risk visibility.
- CI pipeline runs tests on each push/PR.
- Deferred scope is documented instead of silently omitted.

## Risks and Mitigations

- Risk: mock adapter diverges from real OpenStack behavior.
  - Mitigation: adapter protocol abstraction and backlog item for real adapter.
- Risk: lifecycle operations can become asynchronous in production.
  - Mitigation: roadmap includes async task orchestration and operation tracking.
- Risk: non-functional controls (auth, observability) are under-scoped in POC.
  - Mitigation: these are tracked as prioritized near/mid-term items.

