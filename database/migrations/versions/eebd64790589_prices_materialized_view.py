"""prices materialized view

Revision ID: eebd64790589
Revises: 0e72657c0037
Create Date: 2024-05-22 14:46:28.726962

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "eebd64790589"
down_revision: Union[str, None] = "0e72657c0037"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE MATERIALIZED VIEW latest_token_prices AS
        SELECT
            tp.id,
            tp.resource_address,
            tp.usd_price,
            tp.last_updated_at,
            t.allowlist
        FROM
            radix_token_prices tp
        JOIN (
            SELECT
                resource_address,
                MAX(last_updated_at) as last_updated_at
            FROM
                radix_token_prices
            GROUP BY
                resource_address
        ) latest ON tp.resource_address = latest.resource_address AND tp.last_updated_at = latest.last_updated_at
        JOIN radix_tokens t ON tp.resource_address = t.resource_address
                    WHERE
                        t.allowlist = TRUE;
        """
    )


def downgrade() -> None:
    # Drop the materialized view
    op.execute("DROP MATERIALIZED VIEW IF EXISTS latest_token_prices")
