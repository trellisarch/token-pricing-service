"""add ledger token price tables

Revision ID: b1f3a7c9d2e4
Revises: ae02b4606a41
Create Date: 2026-03-17 16:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "b1f3a7c9d2e4"
down_revision: Union[str, None] = "ae02b4606a41"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ledger_token_prices",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("resource_address", sa.String(), nullable=True),
        sa.Column("usd_price", sa.Float(53), nullable=True),
        sa.Column("last_updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "ledger_token_prices_latest",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("resource_address", sa.String(), nullable=True),
        sa.Column("usd_price", sa.Float(53), nullable=True),
        sa.Column("last_updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("resource_address"),
    )


def downgrade() -> None:
    op.drop_table("ledger_token_prices_latest")
    op.drop_table("ledger_token_prices")
