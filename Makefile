.PHONY: test lint typecheck verify api

test:
	cd backend && pytest

lint:
	cd backend && ruff check .

typecheck:
	cd backend && mypy app --strict

verify: test lint typecheck

api:
	cd backend && uvicorn app.main:app --reload
