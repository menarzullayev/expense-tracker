# Contributing

Use small, reviewable changes. Every financial-domain change must include tests for normal behavior, invalid input, authorization boundaries and retry/idempotency semantics.

Required checks before merge:

```bash
cd backend
pytest
ruff check .
mypy app --strict
```

Never commit `.env`, credentials, access tokens, or production database dumps.
