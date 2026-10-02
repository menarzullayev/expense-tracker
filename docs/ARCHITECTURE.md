# Architecture decision record

## ADR-001: exact decimal money

Use Python `Decimal` + PostgreSQL `NUMERIC(20,4)`. Floating point is unsuitable for ledger amounts because decimal fractions may not be represented exactly.

## ADR-002: API-first

The financial domain is exposed through versioned REST endpoints. Telegram, web and future mobile clients consume the same backend rather than duplicating business rules.

## ADR-003: idempotent writes

Financial ingestion endpoints require an idempotency key. This protects against mobile retries, reverse-proxy retries and reconnects creating duplicate expenses.

## ADR-004: migrations are release artifacts

Development can create tables automatically for convenience. Production startup does not mutate schema; migrations are run explicitly before the application becomes ready.
