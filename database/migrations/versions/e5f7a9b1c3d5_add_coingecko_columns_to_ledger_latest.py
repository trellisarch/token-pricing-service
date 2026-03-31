"""add price_source and fetched_at to ledger_token_prices_latest

Revision ID: e5f7a9b1c3d5
Revises: d4e6f8a0b2c3
Create Date: 2026-03-31 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "e5f7a9b1c3d5"
down_revision: Union[str, None] = "d4e6f8a0b2c3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "ledger_token_prices_latest",
        sa.Column("price_source", sa.String(), nullable=True),
    )
    op.add_column(
        "ledger_token_prices_latest",
        sa.Column("fetched_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("ledger_token_prices_latest", "fetched_at")
    op.drop_column("ledger_token_prices_latest", "price_source")
