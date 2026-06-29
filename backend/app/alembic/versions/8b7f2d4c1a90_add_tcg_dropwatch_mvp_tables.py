"""Add TCG DropWatch MVP tables

Revision ID: 8b7f2d4c1a90
Revises: fe56fa70289e
Create Date: 2026-06-29 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "8b7f2d4c1a90"
down_revision = "fe56fa70289e"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table("item")

    op.create_table(
        "product",
        sa.Column("game", sqlmodel.sql.sqltypes.AutoString(length=80), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column(
            "product_type",
            sqlmodel.sql.sqltypes.AutoString(length=120),
            nullable=False,
        ),
        sa.Column("msrp", sa.Float(), nullable=False),
        sa.Column(
            "image_url", sqlmodel.sql.sqltypes.AutoString(length=2048), nullable=True
        ),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_product_game"), "product", ["game"], unique=False)
    op.create_index(op.f("ix_product_name"), "product", ["name"], unique=False)

    op.create_table(
        "retailer_source",
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "retailer_name",
            sqlmodel.sql.sqltypes.AutoString(length=120),
            nullable=False,
        ),
        sa.Column("url", sqlmodel.sql.sqltypes.AutoString(length=2048), nullable=False),
        sa.Column(
            "price_selector",
            sqlmodel.sql.sqltypes.AutoString(length=255),
            nullable=True,
        ),
        sa.Column(
            "stock_selector",
            sqlmodel.sql.sqltypes.AutoString(length=255),
            nullable=True,
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["product_id"], ["product.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_retailer_source_retailer_name"),
        "retailer_source",
        ["retailer_name"],
        unique=False,
    )

    op.create_table(
        "drop_signal",
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("observed_price", sa.Float(), nullable=False),
        sa.Column(
            "stock_status", sqlmodel.sql.sqltypes.AutoString(length=80), nullable=False
        ),
        sa.Column(
            "source_type", sqlmodel.sql.sqltypes.AutoString(length=40), nullable=False
        ),
        sa.Column("url", sqlmodel.sql.sqltypes.AutoString(length=2048), nullable=True),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["product_id"], ["product.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["source_id"], ["retailer_source.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_drop_signal_stock_status"),
        "drop_signal",
        ["stock_status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_drop_signal_source_type"),
        "drop_signal",
        ["source_type"],
        unique=False,
    )

    op.create_table(
        "watchlist",
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("msrp_margin_percent", sa.Float(), nullable=False),
        sa.Column("max_price", sa.Float(), nullable=True),
        sa.Column("email_enabled", sa.Boolean(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["user.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["product.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "alert_event",
        sa.Column("watchlist_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("signal_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "channel", sqlmodel.sql.sqltypes.AutoString(length=40), nullable=False
        ),
        sa.Column("status", sqlmodel.sql.sqltypes.AutoString(length=40), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error", sqlmodel.sql.sqltypes.AutoString(length=2048), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["user.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["signal_id"], ["drop_signal.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["watchlist_id"], ["watchlist.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "watchlist_id",
            "signal_id",
            "channel",
            name="uq_alert_event_watchlist_signal_channel",
        ),
    )
    op.create_index(
        op.f("ix_alert_event_channel"), "alert_event", ["channel"], unique=False
    )
    op.create_index(
        op.f("ix_alert_event_status"), "alert_event", ["status"], unique=False
    )


def downgrade():
    op.drop_index(op.f("ix_alert_event_status"), table_name="alert_event")
    op.drop_index(op.f("ix_alert_event_channel"), table_name="alert_event")
    op.drop_table("alert_event")
    op.drop_table("watchlist")
    op.drop_index(op.f("ix_drop_signal_source_type"), table_name="drop_signal")
    op.drop_index(op.f("ix_drop_signal_stock_status"), table_name="drop_signal")
    op.drop_table("drop_signal")
    op.drop_index(
        op.f("ix_retailer_source_retailer_name"), table_name="retailer_source"
    )
    op.drop_table("retailer_source")
    op.drop_index(op.f("ix_product_name"), table_name="product")
    op.drop_index(op.f("ix_product_game"), table_name="product")
    op.drop_table("product")

    op.create_table(
        "item",
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column("title", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
