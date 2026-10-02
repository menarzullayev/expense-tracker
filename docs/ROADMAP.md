# Production roadmap

## Implemented

- Authentication
- User-scoped accounts
- Categories
- Transactions
- Exact decimal amounts
- Idempotent writes
- Summary and category reporting
- Health/readiness checks
- Docker/PostgreSQL deployment template
- CI gates

## Next production wave

- Refresh-token/session rotation with server-side revocation
- Email verification and password recovery
- Full CRUD with optimistic concurrency controls
- Recurring transaction engine
- Budget envelopes and alerts
- Debt module
- CSV/OFX import with reconciliation and duplicate detection
- Audit log
- Postgres RLS as defense in depth
- Prometheus metrics + Sentry/OpenTelemetry integration
- Redis-backed distributed rate limiting
- Automated database backups and restore verification
- Real bank/Open Banking adapters only after provider contracts are verified
