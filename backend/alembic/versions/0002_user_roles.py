"""add user roles"""
from alembic import op
import sqlalchemy as sa

revision = "0002_user_roles"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("role", sa.String(20), nullable=False, server_default="user"))
    op.create_check_constraint("ck_users_role", "users", "role IN ('user', 'admin', 'root')")


def downgrade() -> None:
    op.drop_constraint("ck_users_role", "users", type_="check")
    op.drop_column("users", "role")
