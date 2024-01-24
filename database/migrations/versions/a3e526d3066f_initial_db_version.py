"""initial db version

Revision ID: a3e526d3066f
Revises: 
Create Date: 2023-12-18 14:36:39.846219

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "a3e526d3066f"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "radix_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("resource_address", sa.String(), nullable=True),
        sa.Column("symbol", sa.String(), nullable=True),
        sa.Column("name", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "radix_token_prices",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("resource_address", sa.String(), nullable=True),
        sa.Column("usd_price", sa.Float(), nullable=True),
        sa.Column("usd_market_cap", sa.Float(), nullable=True),
        sa.Column("usd_vol_24h", sa.Float(), nullable=True),
        sa.Column("last_updated_at", sa.DateTime(), nullable=True),
        sa.Column("token_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["token_id"],
            ["radix_tokens.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("radix_token_prices")
    op.drop_table("radix_tokens")
