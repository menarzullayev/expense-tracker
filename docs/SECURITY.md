# Security model

## Authentication

Passwords are hashed with Argon2id. Access tokens are short-lived JWTs and contain only a user subject and expiry.

## Tenant isolation

Every financial entity is keyed by `user_id` and every query in the authenticated surface applies the current user scope. Cross-user object IDs must not be trusted from the client.

## Money integrity

Amounts are positive input quantities and are persisted as exact `NUMERIC` values. Account balances are derived from opening balance + income - expenses.

## Idempotency

Transaction creation requires an `Idempotency-Key`. A retry with the same key for the same user returns the original transaction instead of creating another financial record.

## Production controls

Place the API behind TLS, set a strong `JWT_SECRET`, restrict CORS to actual frontend origins, configure an external rate limiter, keep secrets out of logs, enable database encryption/backup controls at the provider layer, and test restore procedures regularly.
