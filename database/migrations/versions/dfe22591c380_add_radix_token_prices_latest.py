"""add radix_token_prices_latest

Revision ID: dfe22591c380
Revises: 8ce7cc6d9db1
Create Date: 2025-02-21 12:46:11.244741

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "dfe22591c380"
down_revision: Union[str, None] = "8ce7cc6d9db1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "radix_token_prices_latest",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("resource_address", sa.String, nullable=False),
        sa.Column("usd_price", sa.Float),
        sa.Column("usd_market_cap", sa.Float),
        sa.Column("usd_vol_24h", sa.Float),
        sa.Column("last_updated_at", sa.DateTime(timezone=False)),
        sa.Column("token_id", sa.Integer, unique=True, nullable=False),
    )


def downgrade():
    op.drop_table("radix_token_prices_latest")
