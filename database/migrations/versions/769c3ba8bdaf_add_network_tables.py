"""Add network tables

Revision ID: 769c3ba8bdaf
Revises: bb3ab9c2be89
Create Date: 2024-03-04 21:18:44.526749

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "769c3ba8bdaf"
down_revision: Union[str, None] = "bb3ab9c2be89"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "network",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tx_count_24h", sa.Float(), nullable=False),
        sa.Column("created_accounts_24h", sa.Float(), nullable=False),
        sa.Column("tx_count_7d", sa.Float(), nullable=False),
        sa.Column("created_accounts_7d", sa.Float(), nullable=False),
        sa.Column("tx_count_30d", sa.Float(), nullable=False),
        sa.Column("created_accounts_30d", sa.Float(), nullable=False),
        sa.Column("tx_count_total", sa.Float(), nullable=False),
        sa.Column("created_accounts_total", sa.Float(), nullable=False),
        sa.Column("tvl", sa.Float(), nullable=False),
        sa.Column("staked_xrd", sa.Float(), nullable=False),
        sa.Column("hourly_burnt_amount", sa.Float(), nullable=False),
        sa.Column("daily_burnt_amount", sa.Float(), nullable=False),
        sa.Column("weekly_burnt_amount", sa.Float(), nullable=False),
        sa.Column("monthly_burnt_amount", sa.Float(), nullable=False),
        sa.Column("annually_burnt_amount", sa.Float(), nullable=False),
        sa.Column("remaining_supply", sa.Float(), nullable=False),
        sa.Column("burnt_amount", sa.Float(), nullable=False),
        sa.Column("max_supply", sa.Float(), nullable=False),
        sa.Column("current_block", sa.Float(), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("xrd_market_cap_usd", sa.Float(), nullable=False),
        sa.Column("xrd_total_volume_usd", sa.Float(), nullable=False),
        sa.Column("exrd_market_cap_usd", sa.Float(), nullable=False),
        sa.Column("exrd_total_volume_usd", sa.Float(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("network")
