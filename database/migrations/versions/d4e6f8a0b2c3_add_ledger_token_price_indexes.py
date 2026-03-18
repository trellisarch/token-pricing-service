"""add indexes to ledger_token_prices

Revision ID: d4e6f8a0b2c3
Revises: c3d5e7f9a1b2
Create Date: 2026-03-18 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'd4e6f8a0b2c3'
down_revision: Union[str, None] = 'c3d5e7f9a1b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE INDEX ledger_token_price_idx
        ON ledger_token_prices USING btree (resource_address, last_updated_at DESC)
    """)
    op.execute("""
        CREATE INDEX idx_ledger_token_prices_resource_ts_id
        ON ledger_token_prices USING btree (resource_address, last_updated_at DESC, id DESC)
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_ledger_token_prices_resource_ts_id")
    op.execute("DROP INDEX IF EXISTS ledger_token_price_idx")
