"""copy historical prices from radix_token_prices to ledger_token_prices

Revision ID: c3d5e7f9a1b2
Revises: b1f3a7c9d2e4
Create Date: 2026-03-18 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c3d5e7f9a1b2"
down_revision: Union[str, None] = "b1f3a7c9d2e4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        INSERT INTO ledger_token_prices (resource_address, usd_price, last_updated_at)
        SELECT resource_address, usd_price, last_updated_at
        FROM radix_token_prices
        WHERE resource_address IS NOT NULL
          AND usd_price IS NOT NULL
        ORDER BY last_updated_at
    """)


def downgrade() -> None:
    op.execute("DELETE FROM ledger_token_prices")
