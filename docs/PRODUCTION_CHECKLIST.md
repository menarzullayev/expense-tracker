# Production checklist

## Application
- [x] Exact decimal monetary storage
- [x] Authentication and password hashing
- [x] User-scoped queries
- [x] Idempotent transaction writes
- [x] Request IDs and security response headers
- [x] Health + readiness endpoints
- [x] Explicit production startup guards
- [x] Alembic migrations
- [x] Audit log
- [x] Automated API tests

## Infrastructure before public traffic
- [ ] Create the public GitHub repository and enable branch protection
- [ ] Configure CI repository permissions and required checks
- [ ] Provision managed PostgreSQL
- [ ] Provision secret manager and rotate JWT secret
- [ ] Put API behind TLS/WAF/reverse proxy
- [ ] Add distributed Redis-backed rate limiting
- [ ] Add centralized logs, metrics and alerting
- [ ] Schedule encrypted backups and perform restore drills
- [ ] Configure frontend/API domains and restrictive CORS
- [ ] Configure email verification and password recovery
- [ ] Complete data export/deletion workflow
