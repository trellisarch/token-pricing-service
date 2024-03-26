"""token_price_indexes

Revision ID: 43807e62a606
Revises: 04992dfa3cc8
Create Date: 2024-03-26 09:17:25.038823

"""

from typing import Sequence, Union
from alembic import op
from sqlalchemy import desc


# revision identifiers, used by Alembic.
revision: str = "43807e62a606"
down_revision: Union[str, None] = "04992dfa3cc8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        op.f("token_price_idx"),
        "radix_token_prices",
        ["resource_address", desc("last_updated_at")],
    )

    op.create_index(
        op.f("tokens_with_latest_price_idx"), "radix_tokens", ["resource_address"]
    )


def downgrade() -> None:
    op.drop_index(op.f("token_price_idx"), "radix_token_prices")
    op.drop_index(op.f("tokens_with_latest_price_idx"), "radix_tokens")
