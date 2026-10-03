# Testing Strategy

The Expense Tracker CI is organized around multiple complementary testing strategies.

1. Unit testing — isolated password/security and pure business helpers.
2. Integration testing — auth + accounts + categories + transactions through FastAPI TestClient.
3. API/contract testing — response shape and required fields.
4. Validation testing — invalid amounts, enum values, malformed payloads.
5. Security testing — authentication requirements and unauthorized access.
6. Authorization testing — cross-user tenant isolation.
7. Idempotency testing — exactly-once transaction creation.
8. Boundary testing — inclusive date ranges and pagination limits.
9. Data-integrity testing — balances and category reports reconcile with transactions.
10. Smoke testing — critical API endpoints are reachable.
11. Regression testing — duplicate category and previously fixed behaviors remain protected.
12. Resilience testing — malformed requests fail safely without corrupting state.
13. Performance testing — transaction listing remains within a bounded response-time budget.
14. Static analysis — Ruff and strict Mypy.
15. Frontend type testing — TypeScript noEmit.
16. Frontend build testing — production bundle must compile successfully.
17. End-to-end API workflow testing — a complete user flow is exercised across authentication and finance resources.
18. Deployment verification — Render deployment status and runtime startup logs are checked after release.

Browser-level E2E should be added with Playwright once browser automation is part of the CI environment. API E2E and frontend compilation are already covered without introducing a browser dependency.
