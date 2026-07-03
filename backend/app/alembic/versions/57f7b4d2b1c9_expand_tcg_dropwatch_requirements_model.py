"""Expand TCG DropWatch requirements model

Revision ID: 57f7b4d2b1c9
Revises: 8b7f2d4c1a90
Create Date: 2026-07-03 00:00:00.000000

"""
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "57f7b4d2b1c9"
down_revision = "8b7f2d4c1a90"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "retailer_source",
        sa.Column("label", sqlmodel.sql.sqltypes.AutoString(length=120), nullable=True),
    )
    op.add_column(
        "retailer_source",
        sa.Column(
            "source_kind",
            sqlmodel.sql.sqltypes.AutoString(length=40),
            server_default="retailer_site",
            nullable=False,
        ),
    )
    op.add_column(
        "retailer_source",
        sa.Column("platform", sqlmodel.sql.sqltypes.AutoString(length=80), nullable=True),
    )
    op.add_column(
        "retailer_source",
        sa.Column(
            "account_name", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True
        ),
    )
    op.add_column(
        "retailer_source",
        sa.Column("last_checked_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "retailer_source",
        sa.Column("last_error_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "retailer_source",
        sa.Column(
            "last_error_message",
            sqlmodel.sql.sqltypes.AutoString(length=2048),
            nullable=True,
        ),
    )
    op.add_column(
        "retailer_source",
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.alter_column(
        "retailer_source",
        "product_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=True,
    )
    op.create_index(
        op.f("ix_retailer_source_source_kind"),
        "retailer_source",
        ["source_kind"],
        unique=False,
    )
    op.create_foreign_key(
        "retailer_source_owner_id_fkey",
        "retailer_source",
        "user",
        ["owner_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.add_column(
        "drop_signal",
        sa.Column(
            "retrieved_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.add_column(
        "drop_signal",
        sa.Column(
            "processed_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.add_column(
        "drop_signal",
        sa.Column(
            "processing_status",
            sqlmodel.sql.sqltypes.AutoString(length=40),
            server_default="processed",
            nullable=False,
        ),
    )
    op.create_index(
        op.f("ix_drop_signal_processing_status"),
        "drop_signal",
        ["processing_status"],
        unique=False,
    )

    op.add_column(
        "watchlist",
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
    )
    op.add_column(
        "watchlist",
        sa.Column(
            "notify_on_restock", sa.Boolean(), server_default=sa.true(), nullable=False
        ),
    )
    op.add_column(
        "watchlist",
        sa.Column(
            "notify_on_price_drop",
            sa.Boolean(),
            server_default=sa.true(),
            nullable=False,
        ),
    )
    op.add_column(
        "watchlist",
        sa.Column(
            "notification_cooldown_minutes",
            sa.Integer(),
            server_default="60",
            nullable=False,
        ),
    )

    op.add_column(
        "alert_event",
        sa.Column(
            "error_code", sqlmodel.sql.sqltypes.AutoString(length=80), nullable=True
        ),
    )
    op.add_column(
        "alert_event",
        sa.Column(
            "public_message",
            sqlmodel.sql.sqltypes.AutoString(length=255),
            nullable=True,
        ),
    )


def downgrade():
    op.drop_column("alert_event", "public_message")
    op.drop_column("alert_event", "error_code")

    op.drop_column("watchlist", "notification_cooldown_minutes")
    op.drop_column("watchlist", "notify_on_price_drop")
    op.drop_column("watchlist", "notify_on_restock")
    op.drop_column("watchlist", "is_active")

    op.drop_index(op.f("ix_drop_signal_processing_status"), table_name="drop_signal")
    op.drop_column("drop_signal", "processing_status")
    op.drop_column("drop_signal", "processed_at")
    op.drop_column("drop_signal", "retrieved_at")

    op.drop_constraint(
        "retailer_source_owner_id_fkey", "retailer_source", type_="foreignkey"
    )
    op.drop_index(op.f("ix_retailer_source_source_kind"), table_name="retailer_source")
    op.alter_column(
        "retailer_source",
        "product_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=False,
    )
    op.drop_column("retailer_source", "owner_id")
    op.drop_column("retailer_source", "last_error_message")
    op.drop_column("retailer_source", "last_error_at")
    op.drop_column("retailer_source", "last_checked_at")
    op.drop_column("retailer_source", "account_name")
    op.drop_column("retailer_source", "platform")
    op.drop_column("retailer_source", "source_kind")
    op.drop_column("retailer_source", "label")
