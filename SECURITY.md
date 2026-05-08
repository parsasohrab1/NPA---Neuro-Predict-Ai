# Security Policy

NeuroPredict-AI processes sensitive medical data (PHI). Please treat any
suspected vulnerability as confidential until it has been triaged and patched.

## Supported Versions

| Version | Supported |
| ------- | --------- |
| `main`  | :white_check_mark: |
| Older release branches | :x: |

## Reporting a Vulnerability

Please **do not** open public GitHub issues for security bugs.

- Email: security@example.com (replace before publishing)
- Encrypted reports preferred (PGP key on request)
- Provide: affected component, reproduction steps, impact, and any PoC

We aim to acknowledge reports within **3 business days** and provide an
initial assessment within **10 business days**. Critical issues are
prioritized for an out-of-band patch release.

## Scope

In scope:

- Backend (`/backend`): API, auth, data access, ML inference
- Frontends (`/frontend`, `/admin-dashboard`)
- CI/CD configuration (`.github/workflows`)
- Container images (`Dockerfile`, `docker-compose*.yml`)

Out of scope:

- Denial-of-service via volumetric attacks
- Issues only reproducible on outdated browsers / unsupported environments
- Social engineering or physical attacks

## Hardening Baseline (enforced in CI)

- Static analysis: `bandit -lll` (HIGH must be zero), `ruff`
- Dependency CVE scanning: `pip-audit` (Python), `npm audit --audit-level=high`
- Secrets: `gitleaks` on every push and PR
- SAST: GitHub CodeQL on Python and JS/TS
- Weekly scheduled scans (`Security Scan` workflow)
- Dependabot updates for pip, npm, GitHub Actions, and Docker

## Disclosure

We follow a coordinated disclosure model. Once a fix is released and users
have had a reasonable time to update, we publish an advisory in
`Security and quality` with credit to the reporter (unless they prefer
to remain anonymous).
