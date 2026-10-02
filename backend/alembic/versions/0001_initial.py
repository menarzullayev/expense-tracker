"""initial schema"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("display_name", sa.String(120), nullable=False),
        sa.Column("base_currency", sa.String(3), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=False)
    op.create_table("accounts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("opening_balance", sa.Numeric(20,4), nullable=False),
        sa.Column("is_archived", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_accounts_user_id", "accounts", ["user_id"])
    op.create_table("categories",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("kind", sa.String(10), nullable=False),
        sa.Column("icon", sa.String(20)),
        sa.UniqueConstraint("user_id", "name", "kind", name="uq_category_user_name_kind"),
    )
    op.create_index("ix_categories_user_id", "categories", ["user_id"])
    op.create_table("transactions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("account_id", sa.String(36), sa.ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("category_id", sa.String(36), sa.ForeignKey("categories.id", ondelete="SET NULL")),
        sa.Column("type", sa.String(10), nullable=False),
        sa.Column("amount", sa.Numeric(20,4), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("description", sa.String(500), nullable=False),
        sa.Column("transaction_date", sa.Date(), nullable=False),
        sa.Column("notes", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("idempotency_key", sa.String(255)),
        sa.Column("request_hash", sa.String(64)),
        sa.CheckConstraint("amount > 0", name="ck_transaction_amount_positive"),
        sa.CheckConstraint("type IN ('income', 'expense')", name="ck_transaction_type"),
        sa.UniqueConstraint("user_id", "idempotency_key", name="uq_transaction_user_idempotency"),
    )
    for name, table, column in [
        ("ix_transactions_user_id", "transactions", "user_id"),
        ("ix_transactions_account_id", "transactions", "account_id"),
        ("ix_transactions_category_id", "transactions", "category_id"),
        ("ix_transactions_transaction_date", "transactions", "transaction_date"),
    ]:
        op.create_index(name, table, [column])

    op.create_table("audit_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(50), nullable=False),
        sa.Column("resource_id", sa.String(36)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ip_address", sa.String(64)),
    )
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("transactions")
    op.drop_table("categories")
    op.drop_table("accounts")
    op.drop_table("users")
