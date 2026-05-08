# Summary

<!-- One paragraph: what changes and why. Reference issues with `Fixes #123` if applicable. -->

## Type of change

- [ ] Bug fix
- [ ] New feature
- [ ] Refactor (no behavior change)
- [ ] Documentation
- [ ] CI / build / tooling
- [ ] Security fix

## Scope

- [ ] Backend (`/backend`)
- [ ] Frontend (`/frontend`)
- [ ] Admin dashboard (`/admin-dashboard`)
- [ ] Infra / CI

## How was this tested?

<!-- Describe test commands, manual reproduction, screenshots, etc. -->

## Quality gates

- [ ] All CI jobs pass (`backend`, `frontend`, `secrets-scan`, `docker-build`, `CodeQL`)
- [ ] No new lint, type, or bandit/HIGH findings
- [ ] No new dependency vulnerabilities (`pip-audit`, `npm audit --audit-level=high`)
- [ ] Coverage threshold respected (`backend` ≥ 40 %, ratchet upward over time)
- [ ] Updated docs / `.env.example` if config changed

## Security checklist

- [ ] No secrets, tokens, or PHI in diff (gitleaks-clean)
- [ ] Inputs are validated (Pydantic / zod) and outputs are sanitized
- [ ] Auth / authorization paths reviewed if touched
- [ ] No new SQL string concatenation; use SQLAlchemy parameters
