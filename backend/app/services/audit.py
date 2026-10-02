from sqlalchemy.orm import Session

from app.models import AuditLog


def record_audit(
    db: Session, *, user_id: str | None, action: str, resource_type: str,
    resource_id: str | None = None, ip_address: str | None = None,
) -> None:
    db.add(AuditLog(user_id=user_id, action=action, resource_type=resource_type, resource_id=resource_id, ip_address=ip_address))
