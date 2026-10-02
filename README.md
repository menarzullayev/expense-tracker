# Expense Tracker

Production-oriented, API-first personal finance tracker with strict tenant isolation, exact decimal money values, idempotent transaction creation, reports, health checks, tests, Docker and CI.

## Scope

- Password-based authentication with Argon2id password hashing.
- Accounts with explicit 3-letter currency codes.
- Income and expense transactions.
- User-scoped categories.
- Idempotent transaction ingestion via `Idempotency-Key`.
- Account balance calculation and category expense breakdown.
- Summary reporting over a date range.
- PostgreSQL-ready deployment with Alembic migrations.
- Static zero-dependency web client for fast verification.

## Architecture

```text
Browser / Telegram / future mobile client
                │
                ▼
        FastAPI REST API (/v1)
                │
        ┌───────┴────────┐
        │                │
   Domain validation   Auth/JWT
        │                │
        └───────┬────────┘
                ▼
          SQLAlchemy ORM
                │
                ▼
       PostgreSQL / SQLite
```

Money is stored as SQL `NUMERIC(20,4)` and Python `Decimal`; no floating-point arithmetic is used for financial values.

## Local development

```bash
cd backend
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
pytest
uvicorn app.main:app --reload
```

For PostgreSQL:

```bash
docker compose -f infra/docker-compose.yml up --build
```

Set `JWT_SECRET` to a unique random secret before production. In production, run `alembic upgrade head` as a release step and keep schema creation disabled in application startup.

## API surface

- `POST /v1/auth/register`
- `POST /v1/auth/login`
- `GET /v1/auth/me`
- `GET/POST /v1/finance/accounts`
- `GET/POST /v1/finance/categories`
- `GET/POST /v1/finance/transactions`
- `GET /v1/finance/accounts/{account_id}/balance`
- `GET /v1/finance/reports/category-breakdown`
- `GET /v1/finance/summary`
- `GET /health/live`
- `GET /health/ready`

## Production hardening notes

The repository is intentionally conservative about money semantics and tenancy. Before a public launch, configure a managed secrets store, TLS termination, external rate limiting, centralized structured logs/metrics, backup/restore drills, email verification/password recovery, account deletion/export workflows and an external Redis-backed rate limiter. These are operational dependencies rather than silently mocked application features.
