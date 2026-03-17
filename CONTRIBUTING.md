# Contributing Guide

This project is a proof-of-concept, but it follows lightweight team practices to show production-ready collaboration habits.

## Workflow

1. Create a feature branch from `main`.
2. Keep changes small and focused on one behavior.
3. Open a pull request with:
   - problem statement
   - implementation notes
   - test evidence
   - follow-up backlog items (if any)
4. Require at least one reviewer before merge.

## Definition of Ready (DoR)

A task is ready for implementation when:

- scope is clear and bounded
- acceptance criteria are testable
- dependencies/risks are identified

## Definition of Done (DoD)

A task is done when:

- code is implemented with clear structure
- tests pass locally (`pytest -q`)
- CI passes
- README/docs are updated when behavior changes

## Pull Request Checklist

- [ ] API contract is clear and backward-compatible, or breaking changes are documented
- [ ] Error handling and status codes are intentional
- [ ] Tests cover happy path and key failure path(s)
- [ ] Relevant docs are updated (`README.md`, `docs/*`)
- [ ] Follow-up work is captured in `docs/roadmap-backlog.md`
