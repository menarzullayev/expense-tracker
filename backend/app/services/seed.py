import os
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models import User


@dataclass(frozen=True)
class SeedUser:
    email: str
    display_name: str
    role: str
    password_env: str


DEMO_USERS = (
    SeedUser("demo@expense-tracker.local", "Demo User", "user", "DEMO_PASSWORD"),
    SeedUser("admin@expense-tracker.local", "Admin User", "admin", "ADMIN_PASSWORD"),
    SeedUser("root@expense-tracker.local", "Root User", "root", "ROOT_PASSWORD"),
)


def seed_system_users(db: Session) -> None:
    changed = False
    for spec in DEMO_USERS:
        password = os.getenv(spec.password_env)
        if not password:
            continue
        user = db.scalar(select(User).where(User.email == spec.email))
        if user is None:
            user = User(
                email=spec.email,
                password_hash=hash_password(password),
                display_name=spec.display_name,
                base_currency="UZS",
                role=spec.role,
                is_active=True,
            )
            db.add(user)
            changed = True
        elif user.role != spec.role or not user.is_active:
            user.role = spec.role
            user.is_active = True
            changed = True
    if changed:
        db.commit()
